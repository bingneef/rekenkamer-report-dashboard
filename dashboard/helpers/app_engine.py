from elastic_enterprise_search import AppSearch, exceptions
import streamlit as st
import os
from helpers.minio import put_object, MinioError


class AppEngineError(Exception):
    pass


app_search = AppSearch(
    os.getenv("ENGINE_BASE_URL"),
    http_auth=os.getenv("ENGINE_AUTH")
)

ALL_REPORTS = [
    'rekenkamer',
    'rathenau'
]

ALL_KAMERSTUKKEN = [
    'Verslag van een commissiedebat',
    'Brief regering',
    'Verslag van een wetgevingsoverleg',
    'Motie',
    'Schriftelijke vragen',
    'Verslag van een schriftelijk overleg'
]

default_sources = {
    'all_reports': 'Alle rapporten',
    'rekenkamer': 'Algemene Rekenkamer',
    'rathenau': 'Rathenau',
    'all_kamerstukken': 'Alle kamerstukken',
    'Verslag van een commissiedebat': 'Commissiedebat',
    'Brief regering': 'Kamerbrief',
    'Verslag van een wetgevingsoverleg': 'Wetgevingsoverleg',
    'Motie': 'Motie',
    'Schriftelijke vragen': 'Kamervraag',
    'Verslag van een schriftelijk overleg': 'Schritelijk overleg'
}


@st.experimental_memo
def list_sources():
    env_sources = os.getenv("CUSTOM_SOURCES_MAIN_SEARCH", '')
    if env_sources == '':
        return default_sources

    sources = {}
    for env_source in env_sources.split(','):
        key, name = env_source.split(':')
        sources[key] = name

    return sources


def format_source(sub_source):
    if sub_source in list_sources().keys():
        return list_sources()[sub_source]

    return sub_source


def deflate_group_sources(grouped_sources):
    sources = []
    for grouped_source in grouped_sources:
        if grouped_source == 'all':
            sources.extend(ALL_REPORTS + ALL_KAMERSTUKKEN)
        elif grouped_source == 'all_reports':
            sources.extend(ALL_REPORTS)
        elif grouped_source == 'all_kamerstukken':
            sources.extend(ALL_KAMERSTUKKEN)
        else:
            sources.append(grouped_source)

    return sources


@st.experimental_memo(show_spinner=False, ttl=60)
def search(query, engine_name='source-main', limit=10, filters={}):
    data = app_search.search(
        engine_name=engine_name,
        query=query,
        page_size=limit,
        filters=filters,
        search_fields={
            "title": {
                "weight": 10
            },
            "body": {
                "weight": 1
            },
            "url": {
                "weight": 2
            }
        },
        boosts={
            "relevancy": [
                {
                    "type": "functional",
                    "function": "linear",
                    "operation": "multiply",
                    "factor": 0.5
                }
            ]
        },
        result_fields={
            "id": {"raw": {}},
            "title": {"raw": {}},
            "url": {"raw": {}},
            "doc_source": {"raw": {}},
            "doc_sub_source": {"raw": {}},
            "doc_size": {"raw": {}},
            "extension": {"raw": {}},
            "date": {"raw": {}},
            "meta_detail_url": {"raw": {}}
        }
    )

    results = []
    for result in data['results']:
        try:
            detail_url = result['meta_detail_url']['raw']
        except KeyError:
            detail_url = None

        results.append({
            'id': result['id']['raw'],
            'title': result['title']['raw'],
            'external_url': result['url']['raw'],
            'doc_source': result['doc_source']['raw'],
            'doc_sub_source': format_source(result['doc_sub_source']['raw']),
            'doc_size': result['doc_size']['raw'],
            'detail_url': detail_url,
            'extension': result['extension']['raw'],
            'date': result['date']['raw'],
            'score': result['_meta']['score']
        })

    return results


@st.experimental_memo(show_spinner=False, ttl=60)
def get_engine_stats():
    api_engine = app_search.get_engine(engine_name='source-main')
    total_documents = api_engine['document_count']

    return {
        'total_documents': total_documents
    }


def send_documents_to_external_storage(source_name, documents):
    for document in documents:
        put_object(source_name, document)


def handle_custom_source(source_name, documents):
    print(f"Creating custom source for {source_name} with {len(documents)} document(s)")

    try:
        with st.spinner('Bezig met verwerken..'):
            send_documents_to_external_storage(source_name, documents)

        return True

    except MinioError as error:
        print(error)
        return False


def delete_custom_source_engine(custom_source):
    engine_name = f"source-custom-{custom_source}"
    try:
        app_search.delete_engine(engine_name=engine_name)
    except exceptions.NotFoundError:
        pass


@st.experimental_memo(show_spinner=False, ttl=60)
def custom_sources():
    api_engines = app_search.list_engines()
    custom_engines = []

    for api_engine in api_engines['results']:
        if api_engine['name'].startswith('source-custom-'):
            custom_engines.append(api_engine['name'])

    return custom_engines
