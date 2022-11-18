import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator


@st.experimental_memo
def prep_df_date(df):
    df['date'] = df['date'].apply(lambda x: x.split('T')[0])
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    return df

@st.experimental_memo
def bar_plot(df):
    bins = (df['year'].max() - df['year'].min()) + 1
    labels = np.flip(df['doc_source'].unique())

    sns.set_theme(style="darkgrid")
    fig = plt.figure(figsize=(10, 5))

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
    fig = plt.figure(figsize=(10, 5))
    df_heatmap = df.groupby(['month', 'year'])['id'].count()
    df_heatmap = df_heatmap.reset_index().pivot_table(columns='year', index='month', values='id', fill_value=0)
    df_heatmap = df_heatmap.reindex(np.arange(df['year'].min(), 2023), axis=1, fill_value=0)
    df_heatmap = df_heatmap.reindex(np.arange(1, 13), axis=0, fill_value=0)

    ax = sns.heatmap(
        df_heatmap,
        cmap="rocket_r",
        yticklabels=['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober',
                     'November', 'December']
    )
    ax.set(xlabel='Jaar', ylabel='Maand')
    plt.xticks(rotation=45)
    plt.title("Aantal rapporten per maand en jaar")

    return fig
