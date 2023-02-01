import os

import numpy as np
import pandas as pd
import streamlit as st

from helpers.app_engine import search, search_max_documents, list_sources, format_source, deflate_group_sources
from helpers.config import set_page_config
from helpers.input import focus_first_input
from helpers.plots import prep_df_date, bar_plot, heatmap_plot
from helpers.table import render_results_table

UTILITY_API_URL = os.getenv("UTILITY_API_URL", 'http://localhost:5000')
DEFAULT_SEARCH = os.getenv("DEFAULT_SEARCH", "")

# FIXME: add all filters
if 'extended_search' not in st.session_state:
    st.session_state.extended_search = False

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

    query = col1.text_input('Zoekterm', placeholder="Wat zoek je?", value=DEFAULT_SEARCH,
                            help="Zie de FAQ voor tips voor geavanceerde zoekopdrachten")

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
            tab1, tab2, tab3 = st.tabs(["Documenten 📄", "Grafieken 📊", "Extra opties ⚡️"])

            # Data tab
            with tab1:
                render_results_table(results)

            # Extra tab (zip)
            with tab3:
                load_all_zip = False
                if results['meta']['total_documents'] > len(results['documents']):
                    load_all_zip = st.checkbox("Gebruik alle gevonden resultaten voor de export", value=False,
                                               help="Standaard wordt de limiet van de zoekopdracht gebruikt",
                                               key="load_all_zip")

                keep_folder_structure = st.checkbox("Exporteer documenten in orginele folder structuur", value=False,
                                                    help="Standaard wordt de structuur platgeslagen en komen alle "
                                                         "documenten in dezelfde folder terecht. Deze instelling is "
                                                         "niet van toepassing op publieke bronnen.")

                if st.button("Exporteer bestanden"):
                    if load_all_zip:
                        print("Loading all documents for ZIP")
                        zip_documents = search_max_documents(**search_args,
                                                             result_fields=['id', 's3_path'])
                    else:
                        zip_documents = results

                    def row_to_input_line(row):
                        return f"<input type='hidden' name='document_paths[]' value='{row['s3_path']}' />"

                    filename = f"{query}.zip"
                    markdown_body = f"""
                    <html style="height=0; width=0">
                        <form action="{UTILITY_API_URL}/zip" method="post">
                        <input type='hidden' name='filename' value='{filename}' />
                        <input type='hidden' name='keep_folder_structure' value={1 if keep_folder_structure else 0} />
                        {''.join(list(map(row_to_input_line, zip_documents['documents'])))}
                        <script>
                            document.querySelector('form').submit()
                        </script>
                    </html>
                    """

                    st.components.v1.html(markdown_body)

            # Plot
            with tab2:
                load_all_plots = False
                if results['meta']['total_documents'] > len(results['documents']):
                    load_all_plots = st.checkbox("Gebruik alle gevonden resultaten", value=False,
                                                 help="Standaard wordt de limiet van de zoekopdracht gebruikt",
                                                 key="load_all_plots")

                if load_all_plots:
                    print("Loading all documents for plots")
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
