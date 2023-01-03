import streamlit as st
from helpers.config import set_page_config


def anchor_from_question(question):
    return question.replace(' ', '-').lower()


set_page_config(
    page_title="FAQ",
    page_icon="🤨"
)

st.markdown("# FAQ 🤨")

data = [
    {
        'question': "Vraag 1",
        'answer': "Antwoord 1"
    },
    {
        'question': "Vraag 2",
        'answer': "Antwoord 2"
    },
    {
        'question': "Vraag 3",
        'answer': "Antwoord 3"
    },
    {
        'question': "Vraag 4",
        'answer': "Antwoord 4"
    },
    {
        'question': "Vraag 5",
        'answer': "Antwoord 5"
    }
]


def table_of_contents_str(data):
    return "\\\n".join(
        map(
            lambda item: f"[{item['question']}](#{anchor_from_question(item['question'])})",
            data
        )
    )


st.markdown(table_of_contents_str(data))

for item in data:
    st.subheader(item['question'], anchor=anchor_from_question(item['question']))
    st.markdown(item['answer'])
