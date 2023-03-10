import base64
import os
import time

import requests

AIRFLOW_HOST = os.environ.get("AIRFLOW_HOST", "http://localhost:8080")
AIRFLOW_USERNAME = os.environ.get("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.environ.get("AIRFLOW_PASSWORD", "airflow")


def create_custom_source_job():
    url = f"{AIRFLOW_HOST}/api/v1/dags/source_custom/dagRuns"
    auth_base64 = base64.standard_b64encode(f"{AIRFLOW_USERNAME}:{AIRFLOW_PASSWORD}".encode()).decode()

    response = requests.post(
        url,
        json={
            "dag_run_id": str(time.time()),
            "conf": {}
        },
        headers={
            'Authorization': f'Basic {auth_base64}'
        }
    )

    print(f"Created Airflow job, status code = {response.status_code}")
