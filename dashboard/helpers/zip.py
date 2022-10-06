import requests
import zipfile
import os
import streamlit as st
import hashlib


@st.cache
def generate_dataframe_checksum(df):
    data = df.to_json().encode()
    return hashlib.md5(data).hexdigest()


def zip_ready(df, query):
    zip_file_name = f"{file_root(query)}.zip"
    checksum_file_name = f"{file_root(query)}.hash.txt"
    if os.path.exists(zip_file_name) & os.path.exists(checksum_file_name):
        with open(checksum_file_name) as file:
            checksum = file.read()
            if checksum == generate_dataframe_checksum(df):
                return True
    
    return False


@st.cache
def file_root(query):
    return f"tmp/zips/{query}" 


def download_pdf(row):
        write_path = f"tmp/reports/{row['uid']}.pdf"

        if os.path.exists(write_path) is False:
            r = requests.get(row['url'], allow_redirects=True)

            with open(write_path, 'wb') as file:
                file.write(r.content)


def generate_zip(df, query):
    df.apply(download_pdf, axis=1)

    out_zipfile = zipfile.ZipFile(f"{file_root(query)}.zip", 'w')
    for folder, __, files in os.walk('tmp/reports'):
        for file in files:
            if file.endswith('.pdf'):
                out_zipfile.write(
                    os.path.join(folder, file), 
                    os.path.relpath(os.path.join(folder,file), 'tmp'), 
                    compress_type = zipfile.ZIP_DEFLATED
                )

    out_zipfile.close()
    with open(f"{file_root(query)}.hash.txt", "w+") as file:
        file.write(generate_dataframe_checksum(df))
