import streamlit as st
from helpers.elastic import get_results
from helpers.zip import generate_zip
import os


st.set_page_config(
    page_title="Rapporten zoeker", 
    page_icon="🔎", 
    layout="wide"
)
st.markdown("# Rapporten zoeker 🔎")

col1, col2, col3 = st.columns([1, 0.5, 0.5])

query = col1.text_input('Rapporten zoekterm')
source = col2.selectbox(
    'Welke bron wil je zoeken?',
    ('Alle', 'Rekenkamer', 'Rathenau'))
limit = col3.selectbox(
    'Aantal resultaten',
    (10, 25, 50, 100, 250, 500, 1000))
    

if query is not None and query != '':
    df = get_results(query=query, source=source, limit=limit)
    
    zip_file_name = f"tmp/zips/{query}.zip"
    if os.path.exists(zip_file_name):
        with open(zip_file_name, "rb") as file:
            btn = st.download_button(
                label="Download ZIP",
                data=file,
                file_name=f"{query}.zip",
                mime="application/zip"
            )
    else:
        if st.button('Genereer zipbestand'):
            generate_zip(df, query)

    show_df = df.copy()
    show_df = show_df[['doc_source', 'title', 'created_at', 'url']]
    show_df['created_at'] = show_df['created_at'].apply(lambda x: x.split('T')[0])
    show_df['doc_source'] = show_df['doc_source'].apply(lambda x: x.capitalize())
    show_df = show_df.rename(
        columns={
            'title': "Titel", 
            'doc_source': "Bron", 
            'created_at': "Publicatie datum", 
            'url': "Externe url"
        }
    )

    st.dataframe(show_df, use_container_width=True)
