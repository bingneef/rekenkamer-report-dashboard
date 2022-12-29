# app/Dockerfile

FROM python:3.10-slim

EXPOSE 8501

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["streamlit", "run", "dashboard/01_🔎_Zoeken_algemene_bronnen.py", "--server.port=8501", "--server.address=0.0.0.0"]