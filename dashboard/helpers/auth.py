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

    login_tab, signup_tab = st.tabs(['Inloggen', 'Registreren'])
    with login_tab:
        with st.form(key="login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Inloggen"):
                login_user(email, password)

    with signup_tab:
        with st.form(key="signup_form"):
            display_name = st.text_input("Naam")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            verification_code = st.text_input("Verificatiecode",
                                              help="Je kan een verificatie code aanvragen door een mail te sturen "
                                                   "naar b.steup@rekenkamer.nl")
            if st.form_submit_button("Registreren"):
                signup_user(display_name, email, password, verification_code)

    return False


def login_user(email, password):
    url = f"{UTILITY_API_URL}/api/v1/auth/login"
    resp = requests.post(url, data={'email': email, 'password': password})
    try:
        st.session_state['search_api_key'] = resp.json()['search_api_key']
        st.session_state['display_name'] = resp.json()['display_name']
        st.session_state['document_access_token'] = resp.json()['document_access_token']
        st.success("U bent ingelogd")

        sleep(0.5)
        st.experimental_rerun()
    except (KeyError, JSONDecodeError):
        print(f"Error, status_code: {resp.status_code}")
        st.error("Inloggen mislukt")


def signup_user(display_name, email, password, verification_code):
    url = f"{UTILITY_API_URL}/api/v1/auth/signup"
    resp = requests.post(url, data={
        'email': email,
        'password': password,
        'display_name': display_name,
        'verification_code': verification_code
    })
    try:
        st.session_state['search_api_key'] = resp.json()['search_api_key']
        st.session_state['display_name'] = resp.json()['display_name']
        st.session_state['document_access_token'] = resp.json()['document_access_token']
        st.success("U bent geregistreerd")

        sleep(0.5)
        st.experimental_rerun()
    except (KeyError, JSONDecodeError):
        print(f"Error, status_code: {resp.status_code}")
        st.error("Registreren mislukt")


def users_for_engine(engine):
    url = f"{UTILITY_API_URL}/api/v1/engines/{engine}/users"
    resp = requests.get(url, headers={
        'x-api-key': st.session_state['search_api_key']
    })

    return resp.json()


def remove_user_from_engine(engine, user):
    url = f"{UTILITY_API_URL}/api/v1/engines/{engine}/users/{user}"
    resp = requests.delete(url, headers={
        'x-api-key': st.session_state['search_api_key']
    })

    return resp.json()


def add_user_to_engine(engine, user):
    url = f"{UTILITY_API_URL}/api/v1/engines/{engine}/users"

    resp = requests.post(url, data={
        'email': user
    }, headers={
        'x-api-key': st.session_state['search_api_key']
    })

    return resp.json()
