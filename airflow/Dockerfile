FROM apache/airflow:2.10.5-python3.11
USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install --no-cache-dir --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt "pandas>=2.1,<3.0" "numpy>=1.24" "scikit-learn>=1.3,<2.0" "joblib>=1.3" "mlflow>=2.10,<4.0"
