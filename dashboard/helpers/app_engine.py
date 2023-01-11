import os

import streamlit as st
from elastic_enterprise_search import AppSearch, exceptions

from .minio import put_object, MinioError


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

    # Allow mapping for custom sources
    if f"source-custom-{sub_source}" in list_sources().keys():
        return list_sources()[f"source-custom-{sub_source}"]

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


@st.experimental_memo(show_spinner=False, ttl=60 * 60 * 24)
def search_max_documents(**kwargs):
    results = {'documents': []}

    current_page = 1
    while True:
        print(f"Searching page {current_page}, currently at {(len(results['documents']))} documents")
        search_args = {
            **kwargs,
            'limit': 1000,
            'current_page': current_page
        }
        page_results = search(
            **search_args
        )
        if 'meta' not in results.keys():
            results['meta'] = page_results['meta']

        results['documents'].extend(page_results['documents'])

        all_documents_loaded = len(results['documents']) >= results['meta']['total_documents']
        no_more_new_documents = len(page_results['documents']) == 0

        if all_documents_loaded or no_more_new_documents:
            return results

        current_page += 1


@st.experimental_memo(show_spinner=False, ttl=60)
def search(
    query,
    engine_name='source-main',
    limit=10,
    current_page=1,
    filters={},
    boosts=None,
    result_fields=None
):
    if result_fields is None:
        result_fields = [
            "id",
            "title",
            "url",
            "doc_source",
            "doc_sub_source",
            "doc_size",
            "extension",
            "date",
            "meta_detail_url"
        ]
    # Cannot provide these keys to Elastic if not set, so make them fully optional
    optional_args = {}
    if boosts is not None:
        optional_args['boosts'] = boosts

    result_fields_mapped = {}
    for result_field in result_fields:
        result_fields_mapped[result_field] = {'raw': {}}

    data = app_search.search(
        **optional_args,
        engine_name=engine_name,
        query=query,
        page_size=limit,
        current_page=current_page,
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
        result_fields=result_fields_mapped
    )

    results = []
    for result in data['results']:
        row = {
            'score': result['_meta']['score']
        }

        for result_field in result_fields:
            try:
                row[result_field] = result[result_field]['raw']
            except KeyError:
                row[result_field] = None

        if 'doc_sub_source' in row.keys():
            row['doc_sub_source'] = format_source(row['doc_sub_source'])

        results.append(row)

    print(f"Found {data['meta']['page']['total_results']} result(s) for {query}")

    return {
        'meta': {
            'total_documents': data['meta']['page']['total_results']
        },
        'documents': results
    }


@st.experimental_memo(show_spinner=False, ttl=60)
def get_engine_stats():
    data = app_search.search(
        query="",
        engine_name="source-main",
        page_size=0,
        facets={
            'doc_sub_source': [
                {
                    'type': 'value',
                    'name': 'doc_sub_source_facets',
                    'sort': {'count': 'desc'}
                }
            ]
        }
    )

    sub_source_facets_data = data['facets']['doc_sub_source'][0]['data']
    source_data = map(
        lambda source: {'name': format_source(source['value']), 'document_count': source['count']},
        sub_source_facets_data
    )
    source_data = list(source_data)

    total_documents = sum(item['document_count'] for item in source_data)

    return {
        'total_documents': total_documents,
        'total_sources': len(source_data),
        'sources_data': source_data
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
