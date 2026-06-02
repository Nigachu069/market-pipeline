from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import sys
sys.path.insert(0, '/opt/airflow')
from pipeline.main import main

def notify_failure(context):
    ti = context["task_instance"]
    print(f"The {ti.task_id} in {ti.dag_id} failed with execution time of {context['execution_date']}. ")

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": notify_failure
}

with DAG(
    dag_id = "market_data",
    default_args = default_args, 
    start_date=datetime(2024, 1, 1),
    schedule="0 8 * * 1-5",
    catchup=False
 ): 
    task1 = PythonOperator(
        task_id = "main",
        python_callable = main,
        op_args = [["AMD", "NVDA", "BTC-USD"]])
    
    task1