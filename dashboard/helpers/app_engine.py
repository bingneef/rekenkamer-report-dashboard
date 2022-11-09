from elastic_enterprise_search import AppSearch
import elastic_enterprise_search
import numpy as np
import math
import pandas as pd
import uuid
import streamlit as st
import time
import os
import json
from helpers.state import get_private_engine_name, set_engine_name, clear_engine_name


app_search = AppSearch(
    os.getenv("ENGINE_BASE_URL"),
    http_auth=os.getenv("ENGINE_AUTH")
)


@st.experimental_memo(show_spinner=False)
def search(query, source, limit=10, filters={}):
    engine = source_to_engine_name(source)

    data = app_search.search(
        engine_name=engine, 
        query=query, 
        page_size=limit,
        filters=filters,
        result_fields={
            "id": { "raw": {} },
            "title": { "raw": {} },
            "url": { "raw": {} },
            "doc_source": { "raw": {} },
            "extension": { "raw": {} },
            "date": { "raw": {} }
        }
    )

    results = []
    for result in data['results']:
        results.append({
            'id': result['id']['raw'],
            'title': result['title']['raw'],
            'url': result['url']['raw'],
            'doc_source': result['doc_source']['raw'],
            'extension': result['extension']['raw'],
            'date': result['date']['raw'],
            'score': result['_meta']['score']
        })

    df = pd.DataFrame(
        results, 
        columns=['id', 'title', 'url', 'doc_source', 'extension', 'date', 'score']
    )

    return df


@st.experimental_memo(show_spinner=False)
def get_engine_stats():
    api_engines = app_search.list_engines()

    engines = []
    for api_engine in api_engines['results']:
        if api_engine['type'] != 'default':
            continue
        
        if api_engine['name'].find('private-') == 0:
            continue

        engines.append({
            'name': api_engine['name'],
            'language': api_engine['language'] or 'Universal',
            'document_count': api_engine['document_count'],
        })

    df_engines = pd.DataFrame.from_dict(engines)

    return {
        'total_engines': df_engines.shape[0],
        'total_documents': df_engines['document_count'].sum(),
        'df_engines': df_engines
    }

    return data

def send_documents_to_external_storage(source_name, documents):
    print(source_name)
    print(documents[0])


def handle_custom_source(source_name, documents):
    print(f"Creating custom source for {source_name} with {len(documents)} document(s)")

    with st.spinner('Bezig met verwerken..'):
        send_documents_to_external_storage(source_name, documents)

    # FIXME: Start intervalling
    st.success('Klaar (niet echt)!', icon="✅")


engines = {
    'Alle': 'source-all',
    'Alle rapporten': 'source-public-reports',
    'Alle kamerstukken': 'source-kamerstukken',
    'Rekenkamer': 'source-rekenkamer',
    'Rathenau': 'source-rathenau',
    'Commissie debatten': 'source-kamer-commissiedebatten',
    'Kamervragen': 'source-kamer-kamervragen',
    'Kamerbrieven': 'source-kamer-briefregering',
    'Moties': 'source-kamer-motie',
    'Wetgevingsoverleggen': 'source-kamer-wetgevingsoverleggen'
}

sources = engines.keys()

def source_to_engine_name(source):
    return engines[source]
