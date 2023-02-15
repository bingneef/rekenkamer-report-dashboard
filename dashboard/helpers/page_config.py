import os

import streamlit as st


def set_page_config(**kwargs):
    st.set_page_config(**kwargs)

    if 'display_name' in st.session_state and st.session_state["display_name"] is not None:
        st.sidebar.write(f"Ingelogd als {st.session_state['display_name']}")

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
