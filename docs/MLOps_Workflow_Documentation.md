# MLOps Workflow Documentation — Flight Price Regression

Repository: https://github.com/St-virus1210/travel-analytics-capstone

## Workflow

CSV validation → feature engineering → train Ridge and Random Forest regressors → evaluate held-out MAE/RMSE/R² → persist scikit-learn pipeline with joblib → log runs with MLflow → serve through Flask → use Streamlit UI → package with Docker → deploy API/UI with Kubernetes → schedule retraining with Airflow → test/build with Jenkins.

## Training and metrics

Run `PYTHONPATH=src python -m travel_analytics.train --data-dir data --artifact-dir artifacts`. Training writes `artifacts/flight_price_model.joblib`, `artifacts/gender_classifier.joblib`, hotels/users pickle files and JSON metrics. Regression compares Ridge and Random Forest on a held-out split and selects by MAE. The baseline Random Forest R² is unusually high; perform time-based validation and leakage analysis before claiming generalization. The source dataset does not document currency.

## REST API

Run `PYTHONPATH=src MODEL_DIR=artifacts DATA_DIR=data python -m travel_analytics.api`. Check `GET /health`; test `POST /predict/flight-price` with JSON fields `from`, `to`, `flightType`, `time`, `distance`, `agency`, `date`. The API also exposes a sensitive-attribute academic demonstration at `POST /predict/gender` and historical recommendations at `GET /recommendations`.

## Streamlit

Run `PYTHONPATH=src DATA_DIR=data API_URL=http://127.0.0.1:5000 streamlit run streamlit/app.py`. The dashboard includes dataset overview, hotel recommendations and flight price prediction.

## Docker and MLflow

Run `docker compose up --build`. API: localhost:5000, dashboard: localhost:8501, MLflow: localhost:5001. Make sure real CSV files exist in `data/`. Inspect MLflow runs after executing training with `MLFLOW_TRACKING_URI` configured.

## Kubernetes

Build the API/dashboard images and make them available to the cluster, then run `kubectl apply -f k8s/`. Inspect `kubectl get deployments,pods,services`, verify pods are Ready, and port-forward the API to test `/health`. Manifests are configuration, not proof of a successful deployment.

## Airflow

Run `cd airflow && docker compose up --build`, open localhost:8080, trigger `travel_analytics_model_training`, and inspect the `validate_source_data` and `train_and_log_models` tasks.

## Jenkins

Configure a Jenkins agent with Python and Docker and create a pipeline job from `Jenkinsfile`. Expected stages are checkout, dependency installation, validation, tests, training and Docker build. Optional registry push requires configured credentials.

## Genuine evidence required before submission

Insert screenshots captured from actual successful runs: training metrics/residual plot, API health and prediction, Streamlit output, Docker container status, MLflow experiment/run metrics, Airflow DAG graph and successful task logs, Jenkins stage view, and Kubernetes ready pods/services. This document intentionally does not contain fabricated screenshots. Record any errors and resolve them before marking a stage complete.
