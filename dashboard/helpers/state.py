import streamlit as st


ENGINE_NAME_KEY = 'private-source-key'


def get_private_engine_name():
    if ENGINE_NAME_KEY in st.session_state and st.session_state[ENGINE_NAME_KEY] != '':
        return st.session_state[ENGINE_NAME_KEY]
    else:
        return None


def set_engine_name(value):
    st.session_state[ENGINE_NAME_KEY] = value


def clear_engine_name():
    del st.session_state[ENGINE_NAME_KEY]
    