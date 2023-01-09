import os

import numpy as np
import pandas as pd
import streamlit as st

from helpers.app_engine import search, search_max_documents, list_sources, format_source, deflate_group_sources
from helpers.config import set_page_config
from helpers.input import focus_first_input
from helpers.plots import prep_df_date, bar_plot, heatmap_plot
from helpers.table import render_results_table

# FIXME: add all filters
if 'extended_search' not in st.session_state:
    st.session_state.extended_search = False

if 'query' not in st.session_state:
    st.session_state.query = ""

if os.getenv("CUSTOM_SOURCES_MAIN_SEARCH", '') == '':
    SEARCH_TYPE = 'sources'
else:
    SEARCH_TYPE = 'engines'


def set_extended_search():
    st.session_state.extended_search = st.session_state.extended_search is False


def render_plots(df):
    st.write('# Impact score')
    col1, col2 = st.columns(2)
    col1.write(bar_plot(df, kind='sum'))
    col2.write(heatmap_plot(df, kind='sum'))

    st.write('# Aantal documenten')
    col1, col2 = st.columns(2)
    col1.write(bar_plot(df))
    col2.write(heatmap_plot(df))


def render_form_controls():
    col1, col2, col3 = st.columns([1, 0.5, 0.5])

    query = col1.text_input('Zoekterm', placeholder="Wat zoek je?", value=st.session_state.query)
    st.session_state.query = query

    if SEARCH_TYPE == 'engines':
        input_type = col2.selectbox
    else:
        input_type = col2.multiselect

    sources = input_type(
        'Welke bron(nen) wil je doorzoeken?',
        list_sources().keys(),
        format_func=format_source)

    limit = col3.selectbox(
        'Aantal resultaten',
        (10, 25, 50, 100, 250, 500, 1000),
        index=3)

    return query, sources, limit


def render_extended_form_controls():
    st.checkbox('Uitgebreid zoeken', on_change=set_extended_search, value=st.session_state.extended_search)
    boost_recent = True
    start_year = end_year = None

    if st.session_state.extended_search:
        ad_col1, ad_col2 = st.columns([0.5, 1], gap='large')
        with ad_col2:
            # Hack to ensure vertical alignment
            st.markdown('&nbsp;', unsafe_allow_html=True)
            boost_recent = st.checkbox('Boost recente documenten', help="Geef meer waarde aan recente documenten",
                                       value=True)

        with ad_col1:
            start_year, end_year = st.select_slider(
                'Publicatie jaar',
                options=np.arange(1990, 2024),
                value=(2010, 2023)
            )

    return boost_recent, start_year, end_year


def extended_search_payload(start_year, end_year):
    return [
        {
            "date": {
                "from": f"{start_year}-01-01T00:00:00+00:00",
                "to": f"{end_year}-12-31T23:59:59+00:00"
            }
        }
    ]


def main():
    set_page_config(
        page_title="Zoeken in algemene bronnen",
        page_icon="🔎",
        layout="wide"
    )

    st.markdown("# Zoeken in algemene bronnen🔎")

    query, sources, limit = render_form_controls()
    boost_recent, start_year, end_year = render_extended_form_controls()

    if query is not None and query != '':
        boosts = None
        if boost_recent:
            boosts = {
                "relevancy": [
                    {
                        "type": "functional",
                        "function": "linear",
                        "operation": "multiply",
                        "factor": 0.5
                    }
                ]
            }

        filters = []
        if len(sources) > 0:
            filters.append({'doc_sub_source': deflate_group_sources(sources)})

        if st.session_state.extended_search:
            filters.extend(extended_search_payload(start_year, end_year))

        default_args = {
            'query': query,
            'limit': limit,
            'boosts': boosts
        }

        if SEARCH_TYPE == 'engines':
            # If custom sources are specified, we search the engine
            search_args = {**default_args, 'engine_name': sources}
        else:
            search_args = {**default_args, 'filters': {'all': filters}}

        results = search(**search_args)

        if len(results['documents']) == 0:
            st.write("Geen resultaten gevonden")
        else:
            tab1, tab2 = st.tabs(["Documenten 📄", "Grafieken 📊"])

            # Data tab
            with tab1:
                render_results_table(results)

            # Plot
            with tab2:
                load_all = st.checkbox("Laad alle resultaten", value=False)
                if load_all:
                    print("Loading all documents")
                    plot_results = search_max_documents(**search_args, result_fields=['id', 'doc_sub_source', 'date'])
                else:
                    plot_results = results

                df = pd.DataFrame(
                    plot_results['documents'],
                    columns=['id', 'doc_sub_source', 'date', 'score']
                )
                df = prep_df_date(df)
                render_plots(df)

    focus_first_input()


if __name__ == '__main__':
    main()
