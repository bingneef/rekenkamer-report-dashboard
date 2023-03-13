import os

import streamlit as st

from dashboard.config import ENABLE_CUSTOM_SOURCE_CREATE
from dashboard.helpers.app_engine import handle_custom_source, get_custom_sources
from dashboard.helpers.auth import requires_auth
from dashboard.helpers.input import focus_first_input
from dashboard.helpers.page_config import set_page_config
from dashboard.views.search.form import results_form
from dashboard.views.search.tabs import show_result_tabs, show_manage_tab


def is_valid_engine_name(engine_name):
    allowed_chars = set("0123456789abcdefghijklmnopqrstuvwxyz-")
    if engine_name[0] == '-':
        return False
    if engine_name[-1] == '-':
        return False
    if not set(engine_name).issubset(allowed_chars):
        return False

    return True


def main():
    set_page_config(
        page_title="Zoeken in eigen bron",
        page_icon="🕵️",
        layout="wide"
    )

    st.markdown("# Zoeken in eigen bron 🕵️")

    if os.getenv("ENABLE_CUSTOM_SOURCE_PAGE", 0) != "1" and False:
        st.error('Deze mogelijkheid is voor deze applicatie uitgezet', icon="❌")
        return

    tab1, tab2, tab3 = st.tabs(["Bron doorzoeken", "Bron toevoegen", "Bron beheren"])

    with tab1:
        if len(get_custom_sources()) == 0:
            st.error('Je hebt nog geen toegang tot eigen bronnen', icon="❌")
        else:
            results, search_args, query = results_form(custom_sources=True)
            show_result_tabs(results, search_args, query)

    with tab2:
        if ENABLE_CUSTOM_SOURCE_CREATE is False and False:
            st.error('Deze mogelijkheid is (nog) uitgezet', icon="❌")
        else:
            custom_source_name = st.text_input(
                "Naam",
                "",
                placeholder="Wat is de naam van de bron?",
                help="De naam mag alleen letters, nummers en koppeltekens (-) bevatten "
                     "en mag niet met een koppelteken beginnen of eindigen."
            )

            uploaded_files = st.file_uploader(
                'Zoek in eigen bestanden',
                accept_multiple_files=True,
                disabled=False
            )

            if len(uploaded_files) > 0:
                def handle_submit(documents):
                    custom_source_name_fmt = custom_source_name.lower()
                    if is_valid_engine_name(custom_source_name_fmt) is False:
                        st.error('De naam mag alleen letters, nummers en koppeltekens (-) bevatten '
                                 'en mag niet met een koppelteken beginnen of eindigen.', icon="🚨")
                        return

                    success = handle_custom_source(custom_source_name_fmt, documents)
                    if success:
                        st.success('De documenten worden verwerkt. Dit kan even duren..', icon="✅")
                    else:
                        st.error('Er is iets foutgegaan..', icon="🚨")

                st.button(
                    "Documenten verwerken",
                    on_click=handle_submit,
                    kwargs={'documents': uploaded_files}
                )
    with tab3:
        show_manage_tab()

    focus_first_input()


if __name__ == '__main__':
    requires_auth(main)
