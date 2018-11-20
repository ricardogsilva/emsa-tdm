"""Draft for production DAGs"""

import datetime as dt
import json
import pathlib

from airflow import DAG
from airflow.operators import python_operator
from airflow.operators import subdag_operator
import numpy as np

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": dt.datetime(2018, 11, 1),
    "email": [
        "ricardo.silva@geo-solutions.it"
    ],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": dt.timedelta(minutes=5),
}


def get_settings():
    settings_path = pathlib.Path(__file__).parent / "test-settings.json"
    with settings_path.open() as fh:
        return json.load(fh)


# TODO: Import the tdm-tools module and use it
def some_task(**kwargs):
    print(f"Hi {kwargs}")
    some_grid = np.arange(0, 1000, 2)
    print(some_grid)


def generate_tile_dag(dag_id, settings, dag_params=None):
    dag = DAG(
        dag_id,
        description="A DAG to process stuff for a single spatial tile",
        default_args=default_args,
        params=dag_params
    )
    with dag:
        for vessel_config in settings["vessels"]:
            vessel = vessel_config["name"]
            for sensor_config in vessel_config["sensor_types"]:
                sensor = sensor_config["name"]
                retrieve_data_task = python_operator.PythonOperator(
                    task_id=f"retrieve_{vessel}_{sensor}_data",
                    python_callable=some_task,
                    provide_context=True
                )
                pre_process_sensor_data_task = python_operator.PythonOperator(
                    task_id=f"preprocess_{vessel}_{sensor}_data",
                    python_callable=some_task,
                    provide_context=True
                )
                retrieve_data_task >> pre_process_sensor_data_task
    return dag


def generate_production_dag():
    settings = get_settings()
    dag = DAG(
        "production_draft",
        description="A draft DAG for using airflow inside docker",
        default_args=default_args,
        schedule_interval=dt.timedelta(days=1)
    )
    with dag:
        aggregator_task = python_operator.PythonOperator(
            task_id="aggregator",
            python_callable=some_task,
            provide_context=True
        )
        for tile in range(settings["processing_tiles"]):
            sub_dag_task_id = f"tile{tile:01d}"
            sub_dag_id = f"{dag.dag_id}.{sub_dag_task_id}"
            sub_dag = generate_tile_dag(sub_dag_id, settings)
            sd = subdag_operator.SubDagOperator(task_id=sub_dag_task_id, subdag=sub_dag)
            sd >> aggregator_task
    return dag


prod_dag = generate_production_dag()
