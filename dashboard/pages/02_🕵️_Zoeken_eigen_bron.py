import streamlit as st
import io
import pandas as pd
from helpers.app_engine import search, handle_custom_source
from helpers.state import get_private_engine_name
from helpers.input import focus_first_input


st.set_page_config(
    page_title="Zoeken in eigen bron", 
    page_icon="🕵️", 
    layout="wide"
)


st.markdown("# Zoeken in eigen bron 🕵️")

custom_source_name = st.text_input(
    "Naam",
    "regenboog"
)

uploaded_files = st.file_uploader(
    'Zoek in eigen bestanden', 
    accept_multiple_files=True, 
    disabled=False
)

if len(uploaded_files) > 0:
    st.button(
        "Documenten verwerken", 
        on_click=lambda documents: handle_custom_source(custom_source_name, documents), 
        kwargs={'documents': uploaded_files}
    )
