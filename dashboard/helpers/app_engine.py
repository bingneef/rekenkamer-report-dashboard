from elastic_enterprise_search import AppSearch
import elastic_enterprise_search
import numpy as np
import math
import pandas as pd
import uuid
import streamlit as st
import time
import json
from helpers.state import get_private_engine_name, set_engine_name, clear_engine_name


app_search = AppSearch(
    st.secrets["ENGINE_BASE_URL"],
    http_auth=st.secrets["ENGINE_AUTH"]
)


@st.experimental_memo(show_spinner=False)
def search(query, source, limit=10, filters={}):
    engine = source.lower().replace(" ", "-")
    if engine == 'alle':
        engine = 'all'
    elif engine == 'alle-rapporten':
        engine = 'rapporten'
    elif engine == 'alle-kamerstukken':
        engine = 'kamerstukken'

    data = app_search.search(
        engine_name=engine, 
        query=query, 
        page_size=limit,
        filters=filters
    )

    results = []
    for result in data['results']:
        results.append({
            'uid': result['id']['raw'],
            'title': result['title']['raw'],
            'url': result['url']['raw'],
            'doc_source': result['doc_source']['raw'],
            'extension': result['extension']['raw'],
            'created_at': result['created_at']['raw'],
            'score': result['_meta']['score']
        })

    df = pd.DataFrame(
        results, 
        columns=['uid', 'title', 'url', 'doc_source', 'extension', 'created_at', 'score']
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

def get_private_source_details():
    engine = app_search.get_engine(engine_name=get_private_engine_name())
    return {
        'language': engine['language'],
        'document_count': engine['document_count']
    }


def remove_private_source():
    try:
        app_search.delete_engine(engine_name=get_private_engine_name())
    except elastic_enterprise_search.exceptions.NotFoundError:
        pass
    
    st.success('Private bron verwijderd', icon="✅")
    
    clear_engine_name()


def handle_private_source(documents):
    name = f"private-f{uuid.uuid4()}"

    with st.spinner('Bezig met verwerken..'):
        df = _dataframe_from_documents(documents)
        _create_engine(name=name)
        _add_documents_to_engine(name=name, docs=df)

        # Ensure engine is processed by ES
        time.sleep(2)

    st.success('Private bron verwerkt!', icon="✅")

    set_engine_name(name)

    return name


@st.experimental_memo(show_spinner=False)
def _dataframe_from_documents(documents):
    data = []
    for document in documents:
        data.append({
            "uid": str(uuid.uuid4()),
            "url": document.name,
            "body": document.read().decode("utf-8") ,
            "publish_date": '2022-10-20',
        })

    return pd.DataFrame.from_dict(data)


def _create_engine(name='private-unique', language='nl'):
    app_search.create_engine(
        engine_name=name,
        language=language,
    )

    app_search.put_schema(
        engine_name=name,
        schema={
            "id": "text",
            "title": "text",
            "body": "text",
            "url": "text",
            "last_updated": "date",
            "created_at": "date"
        }
    )


def _doc_to_app_search_doc(doc):
    return {
        "id": doc['uid'],
        "title": '',
        "body": doc['body'],
        "url": doc['url'],
        "last_updated": doc['publish_date'],
        "created_at": doc['publish_date'],
        "doc_source": 'private'
    }


def _add_documents_to_engine(name, docs=None):
    number_of_chunks = math.ceil(len(docs) / 4)
    for index, doc_chunk in enumerate(np.array_split(docs, number_of_chunks)):
        print(f"Writing chunk {index} of {number_of_chunks}")

        app_search.index_documents(
            engine_name=name,
            documents=json.dumps(doc_chunk.apply(_doc_to_app_search_doc, axis=1).to_list())
        )
        