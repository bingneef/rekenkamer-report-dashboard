import streamlit as st
import io
import pandas as pd
from helpers.app_engine import search, get_private_source_details, handle_private_source, remove_private_source
from helpers.state import get_private_engine_name
from helpers.input import focus_first_input


st.set_page_config(
    page_title="Zoeken in eigen bron", 
    page_icon="🕵️", 
    layout="wide"
)


st.markdown("# Zoeken in eigen bron 🕵️")

if get_private_engine_name() is not None:
    st.button(
        "Private bron verwijderen", 
        on_click=remove_private_source
    )
    col1, col2 = st.columns([1, 0.5])

    query = col1.text_input('Documenten zoekterm')
    limit = col2.selectbox(
        'Aantal resultaten',
        (10, 25, 50, 100, 250, 500, 1000),
        index=3)
    
    if query is None or query == '':
        engine_details = get_private_source_details()

        s_col1, s_col2, _ = st.columns([0.5, 0.5, 1])
        s_col1.metric("Aantal documenten", engine_details['document_count'])
        s_col2.metric("Taal", engine_details['language'].upper())
    
    if query is not None and query != '':
        df = search(query=query, source=get_private_engine_name(), limit=limit)

        if df.shape[0] == 0:
            st.write("Geen resultaten gevonden")
        else:
                    
            # Prep datafram
            df['created_at'] = df['created_at'].apply(lambda x: x.split('T')[0])
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['created_at_fmt'] = df['created_at'].dt.strftime('%d-%m-%Y')

            # Dataframe table
            show_df = df[['score', 'url', 'created_at_fmt']]
            show_df = show_df.rename(
                columns={
                    'score': "Score", 
                    'url': "Bestandsnaam",
                    'created_at_fmt': "Creatie datum"
                }
            )

            st.dataframe(show_df, use_container_width=True)

    focus_first_input()
else:
    uploaded_files = st.file_uploader(
        'Zoek in eigen bestanden', 
        type='txt', 
        accept_multiple_files=True, 
        disabled=False
    )

    if len(uploaded_files) > 0:
        st.button(
            "Documenten verwerken", 
            on_click=handle_private_source, 
            kwargs={'documents': uploaded_files}
        )
