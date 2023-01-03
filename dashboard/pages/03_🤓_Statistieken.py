import streamlit as st
from helpers.app_engine import get_engine_stats
from helpers.config import set_page_config

set_page_config(
    page_title="Rapporten zoeker",
    page_icon="🤓"
)

st.markdown("# Statistieken 🤓")

engine_stats = get_engine_stats()

col1, col2 = st.columns(2)
col1.metric("Aantal documenten", engine_stats['total_documents'])
col2.metric("Aantal bronnen", engine_stats['total_sources'])

st.markdown("## Documenten per bron")
number_of_cols = 3
cols = st.columns(number_of_cols)
for index, source in enumerate(engine_stats['sources_data']):
    cols[index % number_of_cols].metric(source['name'], source['document_count'])
