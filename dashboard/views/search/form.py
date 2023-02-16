import os

import numpy as np
import streamlit as st

from dashboard.helpers.app_engine import list_sources, format_source, deflate_group_sources, search

DEFAULT_SEARCH = os.getenv("DEFAULT_SEARCH", "")


def set_extended_search():
    st.session_state.extended_search = st.session_state.extended_search is False


def render_form_controls(custom_sources=False):
    col1, col2, col3 = st.columns([1, 0.5, 0.5])

    query = col1.text_input('Zoekterm', placeholder="Wat zoek je?", value=DEFAULT_SEARCH,
                            help="Zie de FAQ voor tips voor geavanceerde zoekopdrachten")

    if custom_sources:
        input_type = col2.selectbox
        source_annot = 'bron'
    else:
        input_type = col2.multiselect
        source_annot = 'bron(nen)'

    sources = input_type(
        f"Welke {source_annot} wil je doorzoeken?",
        list_sources(custom_sources).keys(),
        format_func=format_source)

    limit = col3.selectbox(
        'Aantal resultaten',
        (10, 25, 50, 100, 250, 500, 1000),
        index=3)

    return query, sources, limit


def render_extended_form_controls():
    if 'extended_search' not in st.session_state:
        st.session_state.extended_search = False

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


def results_form(custom_sources=False):
    query, sources, limit = render_form_controls(custom_sources=custom_sources)
    boost_recent, start_year, end_year = render_extended_form_controls()
    search_args = {}
    results = None

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

        if custom_sources is True:
            # If custom sources are specified, we search the engines
            search_args = {**default_args, 'engine_name': sources}
        else:
            # Otherwise we search the source-main engine
            search_args = {**default_args, 'filters': {'all': filters}}

        results = search(**search_args)

    return results, search_args, query
