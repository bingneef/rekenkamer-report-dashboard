import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


@st.experimental_memo
def prep_df_date(df):
    sns.set_theme(style="darkgrid")

    df['date'] = df['date'].apply(lambda x: x.split('T')[0])
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    return df


@st.experimental_memo
def bar_plot(df, kind='count'):
    fig = plt.figure(figsize=(10, 5))

    df_barplot = df.groupby(['doc_sub_source', 'year'])['score']

    if kind == 'sum':
        df_barplot = df_barplot.sum('score')
    else:
        df_barplot = df_barplot.count()

    df_barplot = df_barplot.reset_index()

    # This is required for the legend
    df_barplot['Bron'] = df_barplot['doc_sub_source']

    ax = sns.barplot(df_barplot, x='year', y='score', hue='Bron')

    if kind == 'sum':
        ylabel = 'Impact score'
    else:
        ylabel = 'Aantal documenten'

    ax.set(xlabel='Jaar', ylabel=ylabel)
    plt.xticks(rotation=45)

    if kind == 'sum':
        plt.title("Impact score per jaar per bron")
    else:
        plt.title("Aantal documenten per jaar per bron")

    return fig


@st.experimental_memo
def heatmap_plot(df, kind='count'):
    fig = plt.figure(figsize=(10, 5))
    df_heatmap = df.groupby(['month', 'year'])['score']

    if kind == 'sum':
        df_heatmap = df_heatmap.sum()
    else:
        df_heatmap = df_heatmap.count()

    df_heatmap = df_heatmap.reset_index().pivot_table(columns='year', index='month', values='score', fill_value=0)

    year_limit = datetime.date.today().year + 1
    df_heatmap = df_heatmap.reindex(np.arange(df['year'].min(), year_limit), axis=1, fill_value=0)
    df_heatmap = df_heatmap.reindex(np.arange(1, 13), axis=0, fill_value=0)

    ax = sns.heatmap(
        df_heatmap,
        cmap="rocket_r",
        yticklabels=['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober',
                     'November', 'December']
    )
    ax.set(xlabel='Jaar', ylabel='Maand')
    plt.xticks(rotation=45)

    if kind == 'sum':
        plt.title("Impact score per maand en jaar")
    else:
        plt.title("Aantal documenten per maand en jaar")

    return fig
