import streamlit as st

from dashboard.helpers.app_engine import get_engine_stats, get_custom_engine_stats
from dashboard.helpers.page_config import set_page_config

set_page_config(
    page_title="Rapporten zoeker",
    page_icon="🤓"
)

st.markdown("# Statistieken 🤓")
tab_public, tab_custom = st.tabs(["Algemene bronnen", "Eigen bronnen"])


def render_stats(engine_stats):
    col1, col2 = st.columns(2)
    col1.metric("Aantal documenten", engine_stats['total_documents'])
    col2.metric("Aantal bronnen", engine_stats['total_sources'])

    if len(engine_stats['sources_data']) == 0:
        return

    st.markdown("### Documenten per bron")
    number_of_cols = 3
    cols = st.columns(number_of_cols)
    for index, source in enumerate(engine_stats['sources_data']):
        cols[index % number_of_cols].metric(source['name'], source['document_count'])


with tab_public:
    render_stats(get_engine_stats())

with tab_custom:
    custom_engine_stats = get_custom_engine_stats()
    if custom_engine_stats['total_sources'] == 0:
        if 'search_api_key' in st.session_state:
            st.error('Je hebt nog geen toegang tot eigen bronnen', icon="❌")
        else:
            st.error('Je bent niet ingelogd', icon="❌")

    else:
        render_stats(custom_engine_stats)
