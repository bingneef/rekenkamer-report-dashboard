from elastic_enterprise_search import AppSearch, exceptions
import pandas as pd
import streamlit as st
import os
from helpers.minio import put_object, MinioError


class AppEngineError(Exception):
    pass


app_search = AppSearch(
    os.getenv("ENGINE_BASE_URL"),
    http_auth=os.getenv("ENGINE_AUTH")
)

public_sources = {
    'Alle': 'source-all',
    'Alle rapporten': 'source-public-reports',
    'Alle kamerstukken': 'source-kamerstukken',
    'Rekenkamer': 'source-rekenkamer',
    'Rathenau': 'source-rathenau',
    'Commissiedebat': 'source-kamer-commissiedebatten',
    'Kamervraag': 'source-kamer-kamervragen',
    'Kamerbrief': 'source-kamer-briefregering',
    'Motie': 'source-kamer-moties',
    'Wetgevingsoverleg': 'source-kamer-wetgevingsoverleggen'
}

sources = public_sources.keys()


@st.experimental_memo(show_spinner=False, ttl=60)
def search(query, engine_name, limit=10, filters={}):
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
            "doc_size": {"raw": {}},
            "extension": {"raw": {}},
            "date": {"raw": {}}
        }
    )

    results = []
    for result in data['results']:
        results.append({
            'id': result['id']['raw'],
            'title': result['title']['raw'],
            'external_url': result['url']['raw'],
            'doc_source': result['doc_source']['raw'],
            'doc_size': result['doc_size']['raw'],
            'extension': result['extension']['raw'],
            'date': result['date']['raw'],
            'score': result['_meta']['score']
        })

    return results


@st.experimental_memo(show_spinner=False, ttl=60)
def get_engine_stats():
    api_engines = app_search.list_engines()

    public_engines = []
    custom_engines = []
    total_documents = 0
    total_engines = 0

    for api_engine in api_engines['results']:
        if api_engine['type'] != 'default':
            continue

        total_documents += api_engine['document_count']
        total_engines += 1

        engine = {
            'name': api_engine['name'].replace('source-', '').replace('custom-', ''),
            'language': api_engine['language'] or 'Universal',
            'document_count': api_engine['document_count'],
        }
        if api_engine['name'].startswith('source-custom-'):
            custom_engines.append(engine)
        else:
            public_engines.append(engine)

    return {
        'total_engines': total_engines,
        'total_documents': total_documents,
        'df_public_engines': pd.DataFrame.from_dict(public_engines).sort_values(by='name').reset_index(drop=True),
        'df_custom_engines': pd.DataFrame.from_dict(custom_engines).sort_values(by='name').reset_index(drop=True)
    }

    return data


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


def public_source_to_engine_name(public_source):
    return public_sources[public_source]
