# Travel Analytics & MLOps Capstone

End-to-end capstone using flight, hotel and user datasets. Flight-price regression is the primary MLOps walkthrough; the project also includes Logistic Regression classification and a historical hotel recommender.

## Components

- src/travel_analytics/train.py: training, hold-out metrics, joblib persistence and optional MLflow logging
- src/travel_analytics/api.py and api/app.py: Flask REST API (/health, /predict/flight-price, /predict/gender, /recommendations)
- streamlit/app.py: dashboard and API-backed UI
- Dockerfile and docker-compose.yml: containerized API, dashboard and MLflow
- airflow/dags/travel_model_training.py: data validation then scheduled training
- Jenkinsfile: tests, training, image build and optional registry push
- k8s/: API and dashboard deployments/services
- tests/: core and API contract tests
- RUNBOOK.md: setup and evidence checklist

## Quick start

Python 3.10–3.12 recommended. Put flights.csv, hotels.csv and users.csv in data/.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python scripts/validate_project.py
PYTHONPATH=src python -m travel_analytics.train --data-dir data --artifact-dir artifacts
PYTHONPATH=src pytest -q
```

Training creates flight_price_model.joblib, gender_classifier.joblib, hotels.pkl, users.pkl and JSON metrics. Flight training compares Ridge and Random Forest and selects by MAE. The current Random Forest score is unusually strong and must be investigated for leakage and generalization using time-based validation before making performance claims.

## API and Streamlit

Terminal 1: `PYTHONPATH=src MODEL_DIR=artifacts DATA_DIR=data python -m travel_analytics.api`

Terminal 2: `PYTHONPATH=src DATA_DIR=data API_URL=http://127.0.0.1:5000 streamlit run streamlit/app.py`

API: http://localhost:5000/health. Dashboard: http://localhost:8501. Run `python scripts/smoke_test_api.py` for smoke tests. The source dataset does not specify currency, so prices are returned in dataset units.

## Docker Compose and MLflow

Run `docker compose up --build`. API is on port 5000, Streamlit on 8501 and MLflow on 5001. Real CSVs must be present in data/. For fresh tracked runs, run the training command in the API container after services start.

## Airflow

Run `cd airflow && docker compose up --build`. Open Airflow at http://localhost:8080; the generated standalone admin password is in container logs. Trigger travel_analytics_model_training and inspect the DAG/task logs. MLflow uses port 5001.

## Jenkins

Configure a Jenkins agent with Python and Docker, then create a Pipeline job from this repository's Jenkinsfile. Registry push is optional and requires DOCKER_REGISTRY plus a Jenkins credential named docker-registry.

## Kubernetes

Build both API and dashboard images, load them into your cluster or push them to a registry and update image names. Apply with `kubectl apply -f k8s/`, then inspect `kubectl get deployments,pods,services`. A manifest is not proof of deployment: capture ready pods and a successful API request from a real cluster.

## Data and model artifacts

The downloadable full project ZIP contains the supplied CSVs and baseline model artifacts. A source-only checkout needs the CSVs in data/ and should run the training command to generate models. Check dataset redistribution permission before committing raw data publicly. Metric JSON files are not a substitute for trained model artifacts.

## Responsible use and evidence

The recorded-gender classifier is a sensitive-attribute academic exercise only and must not be used for decisions about people. Recommendations use historical bookings, not live availability/pricing. Capture genuine screenshots only after each service runs: metrics/residuals, API, Streamlit, Docker, MLflow, Airflow, Jenkins and Kubernetes. See RUNBOOK.md. No remote deployment or screenshot should be claimed without actual execution.
