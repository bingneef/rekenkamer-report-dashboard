import streamlit as st
from helpers.elastic import get_results
from helpers.zip import generate_zip, zip_ready
import os
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from helpers.input import focus_first_input


st.set_page_config(
    page_title="Rapporten zoeker", 
    page_icon="🔎", 
    layout="wide"
)
st.markdown("# Rapporten zoeker 🔎")

col1, col2, col3 = st.columns([1, 0.5, 0.5])

query = col1.text_input('Rapporten zoekterm')
source = col2.selectbox(
    'Welke bron wil je zoeken?',
    ('Alle', 'Rekenkamer', 'Rathenau'))
limit = col3.selectbox(
    'Aantal resultaten',
    (10, 25, 50, 100, 250, 500, 1000),
    index=3)

if query is not None and query != '':
    df = get_results(query=query, source=source, limit=limit)
            
    # Prep datafram
    df['created_at'] = df['created_at'].apply(lambda x: x.split('T')[0])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_at_fmt'] = df['created_at'].dt.strftime('%d-%m-%Y')
    df['doc_source'] = df['doc_source'].apply(lambda x: x.capitalize())
    df['year'] = df['created_at'].dt.year
    df['month'] = df['created_at'].dt.month

    tab1, tab2 = st.tabs(["Data 📄", "Grafieken 📊"])

    # Data tab
    with tab1:
        # Generate/download button
        zip_file_name = f"tmp/zips/{query}.zip"
        if zip_ready(df, query):
            with open(zip_file_name, "rb") as file:
                btn = st.download_button(
                    label="Download ZIP",
                    data=file,
                    file_name=f"{query}.zip",
                    mime="application/zip"
                )
        else:
            st.button('Genereer zipbestand', on_click=lambda: generate_zip(df, query))
        
        # Dataframe table
        show_df = df[['doc_source', 'title', 'created_at_fmt', 'url']]
        show_df = show_df.rename(
            columns={
                'title': "Titel", 
                'doc_source': "Bron", 
                'created_at_fmt': "Publicatie datum", 
                'url': "Externe url"
            }
        )

        st.dataframe(show_df, use_container_width=True)

    # Plot
    with tab2:
        bins = (df['year'].max() - df['year'].min()) + 1
        labels = np.flip(df['doc_source'].unique())

        sns.set_theme(style="darkgrid")
        fig = plt.figure(figsize=(10,5))

        ax = sns.histplot(df, x="year", hue="doc_source", bins=bins, discrete=True, multiple='dodge', legend=True)
        sns.despine()

        ax.set(xlabel='Jaar', ylabel='Aantal rapporten')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(title='Bron', loc='upper left', labels=labels)
        ax.set_xticks(range(df['year'].min(), df['year'].max() + 1))
        plt.xticks(rotation=45)
        plt.title("Aantal rapporten per jaar")

        col1, col2 = st.columns(2)
        col1.write(fig)

        fig = plt.figure(figsize=(10,5))
        df = df.groupby(['month', 'year'])['uid'].count()
        ax = sns.heatmap(
            df.reset_index().pivot_table(columns='year',index='month',values='uid').reindex(np.arange(2000, 2022), axis=1, fill_value=None).reindex(np.arange(1,13), axis=0, fill_value=None), 
            cmap="Greens",
            yticklabels=['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']
        )
        # ax.set_ylim(0, 11)
        col2.write(fig)

focus_first_input()