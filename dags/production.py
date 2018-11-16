"""Draft for production DAGs"""

import datetime as dt

from airflow import DAG
from airflow.operators import python_operator
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


# TODO: Import the tdm-tools module and use it
def some_task(**kwargs):
    print(f"Hi {kwargs}")
    some_grid = np.arange(0, 1000, 2)
    print(some_grid)


production_dag = DAG(
    "production_draft",
    description="A draft DAG for using airflow inside docker",
    default_args=default_args,
    schedule_interval=dt.timedelta(days=1)
)

with production_dag as dag:
    first_task = python_operator.PythonOperator(
        task_id="first",
        python_callable=some_task,
        provide_context=True,
    )

    second_task = python_operator.PythonOperator(
        task_id="second",
        python_callable=some_task,
        provide_context=True,
    )

    first_task >> second_task


