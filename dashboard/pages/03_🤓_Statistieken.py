import streamlit as st
from helpers.app_engine import get_engine_stats
from helpers.config import set_page_config


set_page_config(
    page_title="Rapporten zoeker",
    page_icon="🤓"
)

st.markdown("# Statistieken 🤓")

engine_stats = get_engine_stats()

col1, _ = st.columns(2)
col1.metric("Aantal documenten", engine_stats['total_documents'])
