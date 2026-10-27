"""Weekly data validation and model-training DAG."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
PROJECT="{{ env_var('TRAVEL_PROJECT_DIR','/opt/travel-analytics') }}"
with DAG(dag_id="travel_analytics_model_training",description="Validate CSVs, then train/evaluate models",start_date=datetime(2024,1,1),schedule="@weekly",catchup=False,tags=["travel","mlops"]) as dag:
 validate_data=BashOperator(task_id="validate_source_data",bash_command=f"cd {PROJECT} && PYTHONPATH=src python -c \"from travel_analytics.data import load_data; d=load_data('data'); print({{k: v.shape for k, v in d.items()}})\"")
 train_models=BashOperator(task_id="train_and_log_models",bash_command=f"cd {PROJECT} && PYTHONPATH=src python -m travel_analytics.train --data-dir data --artifact-dir artifacts")
 validate_data >> train_models
