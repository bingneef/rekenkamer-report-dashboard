import streamlit as st

from dashboard.helpers.app_engine import list_sources, format_source
from dashboard.helpers.auth import users_for_engine, remove_user_from_engine, add_user_to_engine, delete_engine, \
    fetch_user_emails
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
    sources = list_sources(custom=True).keys()
    engine = st.selectbox(
        "Welke bron wil je beheren?",
        sources,
        format_func=format_source)

    # List users
    st.markdown("## Huidige gebruikers met toegang")
    engine_users = users_for_engine(engine)

    number_of_cols = 3

    for index, user in enumerate(engine_users):
        if index % number_of_cols == 0:
            cols = st.columns(number_of_cols)

        col = cols[index % number_of_cols]

        # FIXME: Prevent user from deleting him/herself
        col.markdown(f"#### {user}")
        col.button("Verwijderen", key=f"destroy_{user}", on_click=remove_user_from_engine, args=(engine, user))

    # Add user
    st.markdown("## Gebruiker toevoegen")
    users = list(
        filter(
            lambda item: item not in engine_users,
            fetch_user_emails()
        )
    )

    if len(users) == 0:
        st.write("Er zijn geen gebruikers beschikbaar om toe te voegen")
    else:
        selected_user = st.selectbox("Gebruiker toevoegen", users)
        st.button(
            "Toevoegen",
            key="add_user",
            on_click=add_user_to_engine,
            args=(engine, selected_user),
            disabled=user == "")

    # Remove engine
    st.markdown("## Bron verwijderen")
    delete_source_name = st.text_input("Typ de naam van de bron om te verwijderen", "", placeholder=engine[14:])
    st.button("Verwijder bron", key="destroy_engine", on_click=delete_engine, args=(engine,),
              type="primary",
              disabled=delete_source_name != engine[14:])
