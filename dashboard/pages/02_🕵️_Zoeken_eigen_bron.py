import streamlit as st
import pandas as pd
from helpers.app_engine import search, handle_custom_source, custom_sources, delete_custom_source_engine, AppEngineError
from helpers.minio import delete_custom_source_bucket, MinioError
from helpers.config import set_page_config


set_page_config(
    page_title="Zoeken in eigen bron", 
    page_icon="🕵️", 
    layout="wide"
)

if 'add_custom_source' not in st.session_state:
    st.session_state['add_custom_source'] = False

st.markdown("# Zoeken in eigen bron 🕵️")

tab1, tab2, tab3 = st.tabs(["Bron doorzoeken", "Bron toevoegen", "Bron verwijderen"])


@st.experimental_memo(show_spinner=False)
def prep_df(df):
    df['date'] = df['date'].apply(lambda x: x.split('T')[0])
    df['date'] = pd.to_datetime(df['date'])
    df['date_fmt'] = df['date'].dt.strftime('%d-%m-%Y')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    return df


with tab1:
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
        index=3)

    if query is not None and query != '':
        df = search(query=query, engine_name=f"source-custom-{source}", limit=limit)

        if df.shape[0] == 0:
            st.write("Geen resultaten gevonden")
        else:
            # Prep dataframe
            df = prep_df(df)

            # Dataframe table
            show_df = df[['score', 'title', 'date_fmt', 'url']]
            show_df = show_df.rename(
                columns={
                    'score': "Score",
                    'title': "Titel",
                    'date_fmt': "Laatst gewijzigd",
                    'url': "Externe url"
                }
            )

            st.dataframe(show_df, use_container_width=True)

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
