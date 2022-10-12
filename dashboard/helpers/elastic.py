import requests
import json
import pandas as pd
import streamlit as st


ENGINE_BASE_URL = st.secrets["ENGINE_BASE_URL"]
ENGINE_AUTH = st.secrets["ENGINE_AUTH"]


def get_engine_stats():
    url = f"{ENGINE_BASE_URL}/api/as/v1/engines"
    headers = {"Authorization": f"{ENGINE_AUTH}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    engines = []
    for api_engine in data['results']:
        if api_engine['type'] != 'default':
            continue

        engines.append({
            'name': api_engine['name'],
            'document_count': api_engine['document_count'],
        })

    df_engines = pd.DataFrame.from_dict(engines)

    return {
        'total_engines': df_engines.shape[0],
        'total_documents': df_engines['document_count'].sum(),
        'df_engines': df_engines
    }

    return data


def get_results(query, source, limit=10):
    engine = source.lower()
    if engine == 'alle':
        engine = 'rapporten'

    url = f"{ENGINE_BASE_URL}/api/as/v1/engines/{engine}/search"
    headers = {"Authorization": f"{ENGINE_AUTH}"}
    
    data = {
        'query': query,
        'page': {
            "current": 1,
            "size": limit
        }
    }
    response = requests.post(url, headers=headers, json=data)
    data = response.json()

    results = []
    for result in data['results']:
        results.append({
            'uid': result['id']['raw'],
            'title': result['title']['raw'],
            'url': result['url']['raw'],
            'doc_source': result['doc_source']['raw'],
            'created_at': result['created_at']['raw'],
            'score': result['_meta']['score']
        })

    df = pd.DataFrame(
        results, 
        columns=['uid', 'title', 'url', 'doc_source', 'created_at', 'score']
    )

    return df
