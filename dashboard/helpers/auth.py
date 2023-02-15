import os
from time import sleep

import requests
import streamlit as st
from requests import JSONDecodeError

UTILITY_API_URL = os.getenv("UTILITY_API_URL", 'http://localhost:5000')


def requires_auth(body_func):
    if 'search_api_key' in st.session_state and st.session_state["search_api_key"] is not None:
        return body_func()

    st.set_page_config(page_title="Inloggen", page_icon="🔒", layout="centered")
    st.header("Je moet ingelogd zijn om deze pagina te kunnen gebruiken")

    with st.form(key="login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Inloggen"):
            login_user(email, password)

    return False


def login_user(email, password):
    url = f"{UTILITY_API_URL}/auth/login"
    resp = requests.post(url, data={'email': email, 'password': password})
    try:
        st.session_state['search_api_key'] = resp.json()['search_api_key']
        st.session_state['display_name'] = resp.json()['display_name']
        st.session_state['document_access_token'] = resp.json()['document_access_token']
        st.success("U bent ingelogd")
        print(st.session_state)
        sleep(0.5)
        st.experimental_rerun()
    except (KeyError, JSONDecodeError):
        print(f"Error, status_code: {resp.status_code}")
        st.error("Inloggen mislukt")
