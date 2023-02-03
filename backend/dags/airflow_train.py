from datetime import timedelta
from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import pendulum

local_tz = pendulum.timezone("Asia/Seoul")

with DAG(
    dag_id="Model-Train",
    description="train models",
    start_date=datetime(2023, 2, 2, tzinfo=local_tz),
    schedule_interval="0 5 * * *",
    # schedule_interval = '*/1 * * * *',
    tags=["my_dags"],

) as dag:
    t1 = BashOperator(
        task_id='EASE',
        bash_command="cd ../ && python -W ignore recbole_train.py",
        owner='killdong',
        retries=3,
        retry_delay=timedelta(minutes=3),
    )

    t1