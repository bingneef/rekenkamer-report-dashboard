# app/Dockerfile

FROM python:3.11-slim

EXPOSE 8501

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.3.2

RUN pip install poetry==$POETRY_VERSION

COPY poetry.lock pyproject.toml /app/

RUN poetry export --format requirements.txt > requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "-um", "streamlit", "run", "dashboard/01_🔎_Zoeken_algemene_bronnen.py", "--server.port=8501", "--server.address=0.0.0.0"]