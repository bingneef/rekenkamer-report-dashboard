import requests
import json
import pandas as pd
import streamlit as st


ENGINE_BASE_URL = st.secrets["ENGINE_BASE_URL"]
ENGINE_AUTH = st.secrets["ENGINE_AUTH"]


def get_results(query, source):
    engine = source.lower()
    if engine == 'alle':
        engine = 'rapporten'

    url = f"{ENGINE_BASE_URL}/api/as/v1/engines/{engine}/search"
    headers = {"Authorization": f"{ENGINE_AUTH}"}
    
    data = {
        'query': query,
        'page': {
            "current": 1,
            "size": 1_000
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
            'created_at': result['created_at']['raw']
        })

    df = pd.DataFrame(
        results, 
        columns=['uid', 'title', 'url', 'doc_source', 'created_at']
    )

    return df
