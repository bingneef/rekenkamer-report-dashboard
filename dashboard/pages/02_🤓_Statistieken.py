import streamlit as st
from helpers.elastic import get_engine_stats

st.set_page_config(
    page_title="Rapporten zoeker", 
    page_icon="🤓"
)
st.markdown("# Statistieken 🤓")


engine_stats = get_engine_stats()

col1, col2 = st.columns(2)
col1.metric("Aantal bronnen", engine_stats['total_engines'])
col2.metric("Aantal documenten", engine_stats['total_documents'])

df_engines = engine_stats['df_engines']
df_engines = df_engines.rename(
    columns={
        'name': "Naam", 
        'document_count': "Aantal documenten"
    }
)

st.subheader('Bron statistieken')
st.dataframe(df_engines)
