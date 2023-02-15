import streamlit as st

from dashboard.helpers.input import focus_first_input
from dashboard.helpers.page_config import set_page_config
from dashboard.views.search.form import results_form
from dashboard.views.search.tabs import show_result_tabs


def main():
    set_page_config(
        page_title="Zoeken in algemene bronnen",
        page_icon="🔎",
        layout="wide"
    )

    st.markdown("# Zoeken in algemene bronnen🔎")

    results, search_args, query = results_form(custom_sources=False)
    show_result_tabs(results, search_args, query)
    focus_first_input()


if __name__ == '__main__':
    main()
