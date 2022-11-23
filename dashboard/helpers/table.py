import streamlit as st
import webbrowser
from helpers.minio import generate_custom_source_url

col_ratio = [1, 10, 2, 2, 2]


def open_document_url(url):
    webbrowser.open(url)


@st.experimental_memo(ttl=60 * 60 * 24)
def format_source(source):
    mapping = {
        'kamer_moties': ('Motie', 'kamer-motie'),
        'kamer_kamervragen': ('Kamervraag', 'kamer-vraag'),
        'kamer_briefregering': ('Kamerbrief', 'kamer-brief'),
        'kamer_wetgevingsoverleggen': ('Wetgevingsoverleg', 'kamer-wetgevingsoverleg'),
        'kamer_commissiedebatten': ('Commissiedebat', 'kamer-commissiedebat'),
        'rekenkamer': ('AR rapport', 'rekenkamer'),
        'rathenau': ('Rathenau', 'other')
    }

    if source in mapping.keys():
        return mapping[source]

    return source, 'other'


def format_size(size):
    if size < 1000:
        return 'Zeer kort', 'very-low'
    if size < 10_000:
        return '&nbsp;&nbsp;&nbsp;Kort&nbsp;&nbsp;&nbsp;', 'low'
    if size < 100_000:
        return '&nbsp;Middel&nbsp;', 'middle'
    if size < 500_000:
        return '&nbsp;&nbsp;&nbsp;Lang&nbsp;&nbsp;&nbsp;', 'high'

    return 'Zeer lang', 'very-high'


@st.experimental_memo(ttl=60 * 60 * 24)
def format_date(date):
    return date[0:10]


def render_row(row):
    row_str = "|"

    # Score
    row_str += f"{row['score']:.1f}|"

    # Title
    row_str += f"|*{row['title'].strip()}*|"

    # Date
    date_fmt = format_date(row['date'])
    row_str += f"<span class='date'>{date_fmt}</span>|"

    # Source
    source_fmt, source_class = format_source(row['doc_source'])
    row_str += f"<span class='tag {source_class}'>{source_fmt}</span>|"

    # Size
    size_fmt, size_class = format_size(row['doc_size'])
    row_str += f"<span class='tag {size_class}'>{size_fmt}</span>|"

    # Actions
    # Document url
    # FIXME: investigate streamlit-bridge to generate URLs on the fly
    url_fmt = row['external_url']
    if row['doc_source'] == 'custom':
        url_fmt = generate_custom_source_url(row['external_url'])

    row_str += f"<a href='{url_fmt}' target='_blank'>Openen</a>"

    # Document detail url
    if row['detail_url'] is not None:
        row_str += f" <a href='{row['detail_url']}' class='details-link' target='_blank'>Details&nbsp;➞</a>"
    row_str += "|"

    row_str += "\n"
    return row_str


def render_results_table(results):
    st.markdown("""
        <style>
            table thead {
                background-color: #f0f2f6;
            }
            hr { margin: 0 !important }
            p { margin-bottom: 0.25rem !important }
            .date { white-space: nowrap; }
            .tag {
                padding: 2px 8px;
                background-color: #99999999;
                border-radius: 4px;
                color: #FFFFDE;
                white-space: nowrap;
            }           
            .tag.kamer-motie {
                background-color: #FF8E15
            }
            .tag.kamer-vraag {
                background-color: #FFA544
            }
            .tag.kamer-brief {
                background-color: #E68B2A
            }
            .tag.kamer-wetgevingsoverleg {
                background-color: #CC7211
            }
            .tag.kamer-commissiedebat {
                background-color: #99550D
            } 
            .tag.rekenkamer {
                background-color: #3366ff99;
            }
            .tag.very-low {
                color:#333;
                background-color: #69B34C99;
            }
            .tag.low {
                color:#333;
                background-color: #ACB33499;
            }
            .tag.middle {
                color:#333;
                background-color: #FAB73399;
            }
            .tag.high {
                color:#333;
                background-color: #FF8E1599;
            }
            .tag.very-high {
                color:#333;
                background-color: #FF4E1199;
            }
            
            a.details-link {
                background-color: rgb(0,104,201);
                color: white;
                border-radius: 4px;
                padding: 0 4px;
                text-decoration: none;
            }
        </style>
    """, unsafe_allow_html=True)

    markdown_str = "|**Score**|**Titel van het document**|**Datum**|**Bron**|**Doc lengte**|Acties|\n"
    markdown_str += "|---|---|:-:|:-:|:-:|:-:|\n"

    for row in results:
        markdown_str += render_row(row)

    st.markdown(markdown_str, unsafe_allow_html=True)
