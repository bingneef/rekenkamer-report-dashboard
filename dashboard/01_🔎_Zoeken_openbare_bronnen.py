import streamlit as st
import pandas as pd
import numpy as np
from helpers.app_engine import search, sources as engine_sources, public_source_to_engine_name
from helpers.input import focus_first_input
from helpers.config import set_page_config
from helpers.table import render_results_table
from helpers.plots import prep_df_date, bar_plot, heatmap_plot

if 'extended_search' not in st.session_state:
    st.session_state.extended_search = False


def set_extended_search():
    st.session_state.extended_search = st.session_state.extended_search is False


def render_plots(df):
    col1, col2 = st.columns(2)
    col1.write(bar_plot(df))
    col2.write(heatmap_plot(df))


def render_form_controls():
    col1, col2, col3 = st.columns([1, 0.5, 0.5])

    query = col1.text_input('Zoekterm', placeholder="Waar wil je op zoeken?")
    source = col2.selectbox(
        'Welke bron wil je zoeken?',
        engine_sources)

    limit = col3.selectbox(
        'Aantal resultaten',
        (10, 25, 50, 100, 250, 500, 1000),
        index=4)

    return query, source, limit


def render_extended_form_controls():
    st.checkbox('Uitgebreid zoeken', on_change=set_extended_search)
    doc_types = start_year = end_year = None

    if st.session_state.extended_search:
        ad_col1, ad_col2 = st.columns([0.5, 1], gap='large')
        doc_types = ad_col1.multiselect(
            'Soort document',
            ('pdf', 'docx', 'txt'),
            default=['pdf', 'docx', 'txt'])

        start_year, end_year = ad_col2.select_slider(
            'Publicatie jaar',
            options=np.arange(1990, 2023),
            value=(2010, 2022)
        )

    return doc_types, start_year, end_year


def extended_search_payload(doc_types, start_year, end_year):
    return {
        "all": [
            {"extension": doc_types},
            {
                "date": {
                    "from": f"{start_year}-01-01T00:00:00+00:00",
                    "to": f"{end_year}-12-31T23:59:59+00:00"
                }
            }
        ]
    }


def main():
    set_page_config(
        page_title="Zoeken in openbare bronnen",
        page_icon="🔎",
        layout="wide"
    )

    st.markdown("# Zoeken in openbare bronnen🔎")

    query, source, limit = render_form_controls()
    doc_types, start_year, end_year = render_extended_form_controls()

    if query is not None and query != '':
        filters = {}
        if st.session_state.extended_search:
            filters = extended_search_payload(doc_types, start_year, end_year)

        results = search(query=query, engine_name=public_source_to_engine_name(source), limit=limit, filters=filters)

        if len(results) == 0:
            st.write("Geen resultaten gevonden")
        else:
            tab1, tab2 = st.tabs(["Data 📄", "Grafieken 📊"])

            # Data tab
            with tab1:
                render_results_table(results)

            # Plot
            with tab2:
                df = pd.DataFrame(
                    results,
                    columns=['id', 'title', 'url', 'doc_source', 'extension', 'date', 'score']
                )
                df = prep_df_date(df)
                render_plots(df)

    focus_first_input()


if __name__ == '__main__':
    main()
