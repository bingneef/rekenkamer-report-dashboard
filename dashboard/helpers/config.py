import os

import streamlit as st


def set_page_config(**kwargs):
    st.set_page_config(**kwargs)

    allow_tracking = os.getenv('TRACKING_ENABLE', 0) == "1"

    if allow_tracking:
        tracking_domain = os.environ['TRACKING_DOMAIN']
        tracking_host = os.environ['TRACKING_HOST']
        js_snippet = f"<script defer 'data-api={tracking_host}/api/event' data-domain='{tracking_domain}' " \
                     f"src='http://localhost:8080/script.js'></script>"

        st.components.v1.html(js_snippet, height=0, width=0)

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
