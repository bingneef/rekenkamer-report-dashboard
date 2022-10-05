import requests
import zipfile
import os
import streamlit as st


def download_pdf(row):
        write_path = f"tmp/reports/{row['uid']}.pdf"

        if os.path.exists(write_path) is False:
            r = requests.get(row['url'], allow_redirects=True)

            with open(write_path, 'wb') as file:
                file.write(r.content)


def generate_zip(df, query):
    df.apply(download_pdf, axis=1)

    out_zipfile = zipfile.ZipFile(f"tmp/zips/{query}.zip", 'w')
    for folder, __, files in os.walk('tmp/reports'):
 
        for file in files:
            if file.endswith('.pdf'):
                out_zipfile.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), 'tmp'), compress_type = zipfile.ZIP_DEFLATED)

    out_zipfile.close()
