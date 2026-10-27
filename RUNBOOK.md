# Runbook

## Train
\`python -m venv .venv\`, activate it, \`pip install -r requirements.txt\`, then \`PYTHONPATH=src python -m travel_analytics.train --data-dir data --artifact-dir artifacts\`.

## Tests
\`PYTHONPATH=src pytest -q\`. Flask tests require Flask from requirements.txt.

## API and UI
Terminal 1: \`PYTHONPATH=src MODEL_DIR=artifacts DATA_DIR=data python -m travel_analytics.api\`.
Terminal 2: \`PYTHONPATH=src DATA_DIR=data API_URL=http://127.0.0.1:5000 streamlit run streamlit/app.py\`.
API endpoints: GET /health, POST /predict/flight-price, POST /predict/gender (academic sensitive-attribute demo only), GET /recommendations.

## Docker
\`docker compose up --build\`. API http://localhost:5000; Streamlit http://localhost:8501; MLflow http://localhost:5001.

## Airflow
\`cd airflow && docker compose up --build\`; open http://localhost:8080, trigger \`travel_analytics_model_training\`, inspect the DAG and task logs. Capture screenshots only after successful execution.

## Jenkins
Configure a Jenkins agent with Python and Docker. Create a pipeline job from this repository's Jenkinsfile. Registry push is optional and requires registry URL plus configured Jenkins credential.

## Kubernetes
Build the API and dashboard images; load them into the target cluster or push to a registry and update image tags. Run \`kubectl apply -f k8s/\`, then \`kubectl get deployments,pods,services\`. A manifest is not proof of deployment: capture successful pod readiness and an API request from a real cluster.

## Evidence
Capture genuine outputs for training, API, Streamlit, Docker, MLflow, Airflow, Jenkins and Kubernetes. This repository does not contain fabricated screenshots or claims of remote deployments.
