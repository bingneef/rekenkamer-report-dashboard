import streamlit as st

from dashboard.helpers.app_engine import list_sources, format_source
from dashboard.helpers.auth import users_for_engine, remove_user_from_engine, add_user_to_engine
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


def show_manage_tab():
    engine = st.selectbox(
        f"Welke bron wil je beheren?",
        list_sources(custom=True).keys(),
        format_func=format_source)

    st.markdown("## Huidige gebruikers")
    users = users_for_engine(engine)
    for user in users:
        # FIXME: Prevent user from deleting itself (or alert?)
        col1, col2 = st.columns(2)

        col1.write(user)
        col2.button("Verwijderen", key=f"destroy_{user}", on_click=remove_user_from_engine, args=(engine, user))

    st.markdown("## Nieuwe toegang")
    # FIXME: Fetch from database in selectbox?
    user = st.text_input("Gebruiker toevoegen", "", placeholder="Email van de gebruiker")
    st.button(
        "Toevoegen",
        key="add_user",
        on_click=add_user_to_engine,
        args=(engine, user),
        disabled=user == "")
