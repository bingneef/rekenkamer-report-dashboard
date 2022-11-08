import streamlit as st
import os


def set_page_config(**kwargs):
    st.set_page_config(**kwargs)
    
    if os.getenv("ENV") == "PRODUCTION":
        hide_menu_style = """
                <style>
                #MainMenu {visibility: hidden;}
                </style>
                """
        st.markdown(hide_menu_style, unsafe_allow_html=True)