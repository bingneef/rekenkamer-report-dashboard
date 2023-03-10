import webbrowser

import streamlit as st

from dashboard.helpers.auth import UTILITY_API_URL


def generate_custom_source_url(file_name):
    doc_url = f"{UTILITY_API_URL}/private-document/{file_name}"
    try:
        return f"{doc_url}?access_token={st.session_state['document_access_token']}"
    except KeyError:
        return doc_url


def open_document_url(url):
    webbrowser.open(url)


@st.experimental_memo(ttl=60 * 60 * 24)
def class_from_source(source):
    mapping = {
        'Motie': 'kamer-motie',
        'Kamervraag': 'kamer-vraag',
        'Kamerbrief': 'kamer-brief',
        'Wetgevingsoverleg': 'kamer-wetgevingsoverleg',
        'Commissiedebat': 'kamer-commissiedebat',
        'Schritelijk overleg': 'kamer-schriftelijk-overleg',
        'Algemene Rekenkamer': 'rekenkamer',
        'Rathenau': 'rathenau'
    }

    if source in mapping.keys():
        return mapping[source]

    return 'other'


def format_size(size):
    if size <= 1000:
        return 'Zeer kort', 'very-low'
    if size <= 10_000:
        return '&nbsp;&nbsp;&nbsp;Kort&nbsp;&nbsp;&nbsp;', 'low'
    if size <= 100_000:
        return '&nbsp;Middel&nbsp;', 'middle'
    if size <= 500_000:
        return '&nbsp;&nbsp;&nbsp;Lang&nbsp;&nbsp;&nbsp;', 'high'

    return 'Zeer lang', 'very-high'


@st.experimental_memo(ttl=60 * 60 * 24)
def format_date(date):
    return "-".join(date[0:10].split("-")[::-1])


def render_row(row):
    row_str = "|"

    # Score
    row_str += f"{row['score']:.1f}|"

    # Title
    title_fmt = row['title'].strip().replace("\n", " ").replace('*', "\\*")
    row_str += f"|*{title_fmt}*|"

    # Date
    date_fmt = format_date(row['date'])
    row_str += f"<span class='date'>{date_fmt}</span>|"

    # Source
    source_class = class_from_source(row['doc_sub_source'])
    row_str += f"<span class='tag {source_class}'>{row['doc_sub_source']}</span>|"

    # Size
    size_fmt, size_class = format_size(row['doc_size'])
    row_str += f"<span class='tag {size_class}'>{size_fmt}</span>|"

    # Actions:Document url
    url_fmt = row['url']
    if row['doc_source'] == 'custom':
        url_fmt = generate_custom_source_url(row['url'])

    row_str += f"<a href=\"{url_fmt}\" target='_blank'>Openen</a>"

    # Actions:Document detail url
    if row['meta_detail_url'] is not None:
        row_str += f" <a href=\"{row['meta_detail_url']}\" class='details-link' target='_blank'>Details&nbsp;➞</a>"
    row_str += "|"

    row_str += "\n"
    return row_str


def results_tab(results):
    st.markdown("""
        <style>
            table thead {
                background-color: #f0f2f6;
            }
            hr { margin: 0 !important }
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
            .tag.kamer-schriftelijk-overleg {
                background-color: #DE903E
            }
            .tag.rekenkamer {
                background-color: #3366ff99;
            }
            .tag.rathenau {
                background-color: #ff000099;
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

    for row in results['documents']:
        markdown_str += render_row(row)

    total_documents = results['meta']['total_documents']
    if total_documents == 1:
        results_annot = 'document'
    else:
        results_annot = 'documenten'

    post_annot = ""
    if total_documents > len(results['documents']):
        post_annot = f" ({len(results['documents'])} getoond)"

    st.markdown(f"*{total_documents} {results_annot} gevonden{post_annot}*")
    st.markdown(markdown_str, unsafe_allow_html=True)
