import streamlit as st

from dashboard.config import UTILITY_API_URL
from dashboard.helpers.app_engine import search_max_documents


def _row_to_input_line(row):
    return f"<input type='hidden' name='document_paths[]' value='{row['s3_path']}' />"


def zip_tab(results, search_args, query):
    load_all_zip = False
    if results['meta']['total_documents'] > len(results['documents']):
        load_all_zip = st.checkbox("Gebruik alle gevonden resultaten voor de export", value=False,
                                   help="Standaard wordt de limiet van de zoekopdracht gebruikt",
                                   key="load_all_zip")

    keep_folder_structure = st.checkbox("Exporteer documenten in orginele folder structuur", value=False,
                                        help="Standaard wordt de structuur platgeslagen en komen alle "
                                             "documenten in dezelfde folder terecht.")

    if st.button("Exporteer bestanden"):
        if load_all_zip:
            print("Loading all documents for ZIP")
            zip_documents = search_max_documents(**search_args,
                                                 result_fields=['id', 's3_path'])
        else:
            zip_documents = results

        filename = f"{query}.zip"
        keep_folder_structure_fmt = 1 if keep_folder_structure else 0

        zip_url = f"{UTILITY_API_URL}/zip"
        if 'document_access_token' in st.session_state:
            zip_url = f"{zip_url}?access_token={st.session_state['document_access_token']}"

        markdown_body = f"""
        <html style="height=0; width=0">
            <form action="{zip_url}" method="post">
            <input type='hidden' name='filename' value='{filename}' />
            <input type='hidden' name='keep_folder_structure' value={keep_folder_structure_fmt} />
            {''.join(list(map(_row_to_input_line, zip_documents['documents'])))}
            <script>
                document.querySelector('form').submit()
            </script>
        </html>
        """

        st.components.v1.html(markdown_body)
