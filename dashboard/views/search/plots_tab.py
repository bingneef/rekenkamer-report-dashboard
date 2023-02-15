import pandas as pd
import streamlit as st

from dashboard.helpers.app_engine import search_max_documents
from dashboard.helpers.plots import bar_plot, heatmap_plot, prep_df_date


def _render_plots(df):
    st.write('# Impact score')
    col1, col2 = st.columns(2)
    col1.write(bar_plot(df, kind='sum'))
    col2.write(heatmap_plot(df, kind='sum'))

    st.write('# Aantal documenten')
    col1, col2 = st.columns(2)
    col1.write(bar_plot(df))
    col2.write(heatmap_plot(df))


def plots_tab(results, search_args):
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
    _render_plots(df)
