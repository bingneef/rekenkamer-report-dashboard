import streamlit as st
import pandas as pd
from helpers.app_engine import search, handle_custom_source, custom_sources, delete_custom_source_engine, AppEngineError
from helpers.minio import delete_custom_source_bucket, MinioError
from helpers.config import set_page_config
from helpers.table import render_results_table

if 'add_custom_source' not in st.session_state:
    st.session_state['add_custom_source'] = False

set_page_config(
    page_title="Zoeken in eigen bron",
    page_icon="🕵️",
    layout="wide"
)

st.markdown("# Zoeken in eigen bron 🕵️")


def render_form_controls():
    col1, col2, col3 = st.columns([1, 0.5, 0.5])
    engine_sources = list(
        map(
            lambda x: x.replace('source-custom-', ''),
            custom_sources()
        )
    )

    query = col1.text_input('Zoekterm', placeholder="Waar wil je op zoeken?")
    source = col2.selectbox(
        'Welke bron wil je zoeken?',
        engine_sources)

    limit = col3.selectbox(
        'Aantal resultaten',
        (10, 25, 50, 100, 250, 500, 1000),
        index=4)

    return query, source, limit


def main():
    tab1, tab2, tab3 = st.tabs(["Bron doorzoeken", "Bron toevoegen", "Bron verwijderen"])

    with tab1:
        query, source, limit = render_form_controls()

        if query is not None and query != '':
            results = search(query=query, engine_name=f"source-custom-{source}", limit=limit)

            if len(results) == 0:
                st.write("Geen resultaten gevonden")
            else:
                render_results_table(results)

    with tab2:
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
                allowed_chars = set("0123456789abcdefghijklmnopqrstuvwxyz-")
                if not set(custom_source_name_fmt).issubset(allowed_chars) \
                        or custom_source_name_fmt[-1] == '-' \
                        or custom_source_name_fmt[0] == '-':
                    st.error('De naam mag alleen letters, nummers en koppeltekens (-) bevatten '
                             'en mag niet met een koppelteken beginnen of eindigen.', icon="🚨")
                    return

                success = handle_custom_source(custom_source_name_fmt, documents)
                if success:
                    st.success('De documenten worden verwerkt. Dit kan even duren.', icon="✅")
                else:
                    st.error('Er is iets foutgegaan..', icon="🚨")

            st.button(
                "Documenten verwerken",
                on_click=handle_submit,
                kwargs={'documents': uploaded_files}
            )
    with tab3:
        def handle_delete(custom_source_to_remove):
            try:
                delete_custom_source_engine(custom_source_to_remove)
                delete_custom_source_bucket(custom_source_to_remove)

                st.success(f"Bron {custom_source_to_remove} is verwijderd of bestond niet meer", icon="✅")
            except (AppEngineError, MinioError) as error:
                st.error('Er is iets foutgegaan..', icon="🚨")

        custom_source = st.text_input(
            'Welke bron wil je verwijderen?',
            placeholder="naam-van-bron",
            help="Zorg dat je niet de verkeerde bron verwijdert")

        st.button(
            "Bron verwijderen",
            on_click=handle_delete,
            kwargs={'custom_source_to_remove': custom_source}
        )


if __name__ == '__main__':
    main()
