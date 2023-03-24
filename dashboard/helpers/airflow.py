import base64
import os
import time

import requests

AIRFLOW_HOST = os.environ.get("AIRFLOW_HOST", "http://localhost:8080")
AIRFLOW_USERNAME = os.environ.get("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.environ.get("AIRFLOW_PASSWORD", "airflow")

IN_PROGRESS_STATES = ['running', 'queued', 'scheduled']


def _headers():
    auth_base64 = base64.standard_b64encode(f"{AIRFLOW_USERNAME}:{AIRFLOW_PASSWORD}".encode()).decode()

    return {
        'Authorization': f'Basic {auth_base64}'
    }


def create_custom_source_job(source='') -> bool:
    response = requests.post(
        url=f"{AIRFLOW_HOST}/api/v1/dags/source_custom/dagRuns",
        json={
            "dag_run_id": str(time.time()),
            "conf": {
                'single_custom_source_name': source
            }
        },
        headers=_headers()
    )

    print(f"Created Airflow job, status code = {response.status_code}")

    return response.json()['dag_run_id']


def wait_for_source_to_finish(source):
    if check_custom_source_in_progress(source):
        time.sleep(1)
        return wait_for_source_to_finish(source)


def check_custom_source_in_progress(source: str) -> bool:
    in_progress_stats = ",".join(IN_PROGRESS_STATES)
    response = requests.get(
        url=f"{AIRFLOW_HOST}/api/v1/dags/source_custom/dagRuns?state={in_progress_stats}",
        headers=_headers()
    )

    source_without_prefix = source[14:]
    for dag_run in response.json()['dag_runs']:
        if dag_run['conf']['single_custom_source_name'] == source_without_prefix:
            return True

        # When no source is specified, it runs in multi mode
        if dag_run['conf']['single_custom_source_name'] == '':
            return True

    return False
