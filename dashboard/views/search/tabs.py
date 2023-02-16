import streamlit as st

from dashboard.views.search.plots_tab import plots_tab
from dashboard.views.search.results_tab import results_tab
from dashboard.views.search.zip_tab import zip_tab


def show_result_tabs(results, search_args, query):
    if results is None:
        return

    if len(results['documents']) == 0:
        st.write("Geen resultaten gevonden")
    else:
        tab1, tab2, tab3 = st.tabs(["Documenten 📄", "Grafieken 📊", "Exporteren ⚡️"])

        # Results tab
        with tab1:
            results_tab(results)

        # Extra tab (zip)
        with tab3:
            zip_tab(results=results, search_args=search_args, query=query)

        # Plot
        with tab2:
            plots_tab(results=results, search_args=search_args)
