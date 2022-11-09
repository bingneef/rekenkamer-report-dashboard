import streamlit as st
import os


def set_page_config(**kwargs):
    st.set_page_config(**kwargs)

    custom_style = """
        <style>
            footer {display: none !important}
        </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)
    
    if os.getenv("ENV") == "PRODUCTION":
        hide_menu_style = """
            <style>
                #MainMenu {display: none}
                .stException pre {display: none}
            </style>
        """
        st.markdown(hide_menu_style, unsafe_allow_html=True)