import streamlit as st
import os
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import numpy as np
from helpers.app_engine import search
from helpers.zip import generate_zip, zip_ready
from helpers.input import focus_first_input


if 'extended_search' not in st.session_state:
    st.session_state.extended_search = False

def set_extended_search():
    st.session_state.extended_search = st.session_state.extended_search == False


def zip_button(df, query, c):
    # Generate/download button
    zip_file_name = f"tmp/zips/{query}.zip"
    if zip_ready(df, query):
        with open(zip_file_name, "rb") as file:
            c.download_button(
                label="Download ZIP",
                data=file,
                file_name=f"{query}.zip",
                mime="application/zip"
            )
    else:
        c.button('Genereer zipbestand', on_click=lambda: generate_zip(df, query))


@st.experimental_memo
def bar_plot(df):
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
    plt.title("Aantal rapporten per jaar per bron")

    return fig


@st.experimental_memo
def heatmap_plot(df):
    fig = plt.figure(figsize=(10,5))
    df_heatmap = df.groupby(['month', 'year'])['uid'].count()
    df_heatmap = df_heatmap.reset_index().pivot_table(columns='year',index='month',values='uid', fill_value=0)
    df_heatmap = df_heatmap.reindex(np.arange(df['year'].min(), 2023), axis=1, fill_value=0)
    df_heatmap = df_heatmap.reindex(np.arange(1,13), axis=0, fill_value=0)

    ax = sns.heatmap(
        df_heatmap, 
        cmap="rocket_r",
        yticklabels=['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']
    )
    ax.set(xlabel='Jaar', ylabel='Maand')
    plt.xticks(rotation=45)
    plt.title("Aantal rapporten per maand en jaar")

    return fig


def df_plots(df):
    col1, col2 = st.columns(2)
    col1.write(bar_plot(df))
    col2.write(heatmap_plot(df))


@st.experimental_memo(show_spinner=False)
def prep_df(df):
    df['created_at'] = df['created_at'].apply(lambda x: x.split('T')[0])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_at_fmt'] = df['created_at'].dt.strftime('%d-%m-%Y')
    df['doc_source'] = df['doc_source'].apply(lambda x: x.capitalize())
    df['year'] = df['created_at'].dt.year
    df['month'] = df['created_at'].dt.month

    return df


st.set_page_config(
    page_title="Zoeken in openbare bronnen", 
    page_icon="🔎", 
    layout="wide"
)

st.markdown("# Zoeken in openbare bronnen🔎")

col1, col2, col3 = st.columns([1, 0.5, 0.5])

query = col1.text_input('Zoekterm')
source = col2.selectbox(
    'Welke bron wil je zoeken?',
    ('Alle', 'Alle rapporten', 'Alle kamerstukken', 'Rekenkamer', 'Rathenau', 'CE Delft', 'Commissie debatten', 'Kamervragen', 'Kamerbrieven', 'Moties', 'Wetgevingsoverleggen'))
limit = col3.selectbox(
    'Aantal resultaten',
    (10, 25, 50, 100, 250, 500, 1000),
    index=3)

st.checkbox('Uitgebreid zoeken', on_change=set_extended_search)
if st.session_state.extended_search:
    ad_col1, ad_col2 = st.columns([0.5, 1], gap='large')
    doc_types = ad_col1.multiselect(
        'Soort document',
        ('pdf', 'docx', 'txt'),
        default=['pdf', 'docx', 'txt'])

    start_year, end_year = ad_col2.select_slider(
        'Publicatie jaar',
        options=np.arange(1990, 2023),
        value=(2010, 2022)
    )

if query is not None and query != '':
    filters = {}
    if st.session_state.extended_search:
        filters = {
            "all": [
                { "extension": doc_types },
                { 
                    "created_at": {
                        "from": f"{start_year}-01-01T00:00:00+00:00",
                        "to": f"{end_year}-12-31T23:59:59+00:00"
                    }
                }
            ]
        }

    df = search(query=query, source=source, limit=limit, filters=filters)

    if df.shape[0] == 0:
        st.write("Geen resultaten gevonden")
    else:
                
        # Prep datafram
        df = prep_df(df)

        tab1, tab2 = st.tabs(["Data 📄", "Grafieken 📊"])

        # Data tab
        with tab1:
            c = st.container()
            zip_button(df, query, c)
            
            # Dataframe table
            show_df = df[['score', 'doc_source', 'title', 'created_at_fmt', 'url']]
            show_df = show_df.rename(
                columns={
                    'score': "Score", 
                    'title': "Titel", 
                    'doc_source': "Bron", 
                    'created_at_fmt': "Publicatie datum", 
                    'url': "Externe url"
                }
            )

            c.dataframe(show_df, use_container_width=True)

        # Plot
        with tab2:
            df_plots(df)
            

focus_first_input()
