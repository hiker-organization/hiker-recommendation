# dags/pipeline_recomendacao.py
import sys
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, "/opt/airflow/pipeline")
import main

with DAG(
    dag_id="pipeline_recomendacao",
    start_date=datetime(2026, 1, 1),
    schedule="@weekly",
    catchup=False,
) as dag:
    PythonOperator(task_id="executar_pipeline", python_callable=main.executar)