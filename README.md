# Travel Analytics & MLOps Capstone

End-to-end capstone using `flights.csv`, `hotels.csv`, and `users.csv`:
- Flight-price regression (scikit-learn; MLflow tracking)
- Recorded-gender classification (scikit-learn; MLflow tracking)
- Hotel recommendation (preference/history-based, with popularity fallback)
- Flask REST API
- Streamlit dashboard
- Docker and Docker Compose
- Kubernetes manifests
- Airflow training DAG
- Jenkins CI/CD pipeline
- Pytest checks

## Data inspected

The supplied files were inspected before packaging:
- `flights.csv`: 271,888 rows × 10 columns
- `hotels.csv`: 40,552 rows × 8 columns
- `users.csv`: 1,340 rows × 5 columns
- Initial missing-value scan: zero missing values in each file.

The application rechecks data on startup/training. Dataset sizes may change if you replace the files.

## Quick start (Python 3.10–3.12 recommended)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
python -m travel_analytics.train --data-dir data --artifact-dir artifacts
```

The training command fits the regression and classification models, writes metrics/model artifacts, and logs experiments to MLflow if configured. Without `MLFLOW_TRACKING_URI`, MLflow uses its local default tracking store (the `mlruns/` directory).

Start the API (in another terminal):

```bash
export PYTHONPATH=src
export MODEL_DIR=artifacts
python -m travel_analytics.api
```

Windows PowerShell:
```powershell
$env:PYTHONPATH="src"
$env:MODEL_DIR="artifacts"
python -m travel_analytics.api
```

API is available at `http://localhost:5000`. Health check:
```bash
curl http://localhost:5000/health
```

Start the dashboard:
```bash
export PYTHONPATH=src
streamlit run src/travel_analytics/dashboard.py
```
Open the URL printed by Streamlit (normally `http://localhost:8501`).

## API endpoints

### `POST /predict/flight-price`
```json
{
  "from": "Recife (PE)",
  "to": "Florianopolis (SC)",
  "flightType": "firstClass",
  "time": 1.76,
  "distance": 676.53,
  "agency": "FlyingDrops",
  "date": "2019-09-26"
}
```
Returns a predicted price in the same units as the source `price` column.

### `POST /predict/gender`
```json
{"age": 30, "company": "4You"}
```
Returns the predicted recorded gender class and class probabilities where available. This is a demonstration/educational model only; gender inference is sensitive, can encode dataset bias, and should not be used for consequential decisions. Do not send names or identifiers.

### `GET /recommendations?user_code=0&place=Salvador%20(BH)&max_price=350&limit=5`
Returns hotels ranked using historical user preferences, place/price constraints, and global popularity fallback. Recommendations are not proof of availability or live pricing.

## Train and evaluate

```bash
python -m travel_analytics.train --data-dir data --artifact-dir artifacts
```

Regression metrics: MAE, RMSE, R². Classification metrics: accuracy, balanced accuracy, macro F1, and a classification report. A held-out random split is used by default. For production assessment, consider time-based validation and segment-level error analysis. Metrics are generated when you run training; no unexecuted performance claims are made here.

Modeling notes:
- Flight `price` is the regression target. `travelCode` and `userCode` are excluded as identifier/leakage-prone features.
- Date is converted into year/month/day-of-week features.
- Gender target is `users.gender`; `name` and `code` are excluded. This remains a sensitive-attribute prediction task and is included only to satisfy the academic brief.
- Hotel recommendations use observed bookings, aggregate hotel/place statistics, and user history. This is a lightweight recommender, not a trained neural ranking model.
- Input categories unseen during training are handled by one-hot encoders with `handle_unknown="ignore"`.

## MLflow UI

```bash
mlflow ui --backend-store-uri ./mlruns --host 0.0.0.0 --port 5001
```
Open `http://localhost:5001`.

## Docker Compose

```bash
docker compose up --build
```
This starts the API and dashboard. The API container trains models on first start if artifacts are absent; this can take several minutes. For repeatable deployments, train as a separate release step and persist versioned artifacts. MLflow tracking is optional and not included as a service by default.

## Airflow

The DAG is in `airflow/dags/travel_model_training.py`. Copy it into your Airflow DAGs folder and configure the Airflow environment so the repository and dependencies are available. The DAG runs the training command; configure paths for your Airflow deployment.

## Jenkins

The `Jenkinsfile` installs dependencies, runs tests, trains models, builds the Docker image, and optionally pushes/deploys only when Jenkins credentials and environment variables are configured. Configure `DOCKER_IMAGE`, registry credentials, and deployment stages for your environment before enabling production deployment.

## Kubernetes

The `k8s/` manifests define a Deployment and Service for the API. Build/push the image, update the image name, and make trained artifacts available to the container (the example mounts a PVC). Then:
```bash
kubectl apply -f k8s/
kubectl get pods,svc
```
For production, use a secret manager, resource requests/limits, readiness/liveness probes, TLS/ingress, autoscaling, persistent artifact storage, and a model promotion strategy.

## Repository layout

```text
src/travel_analytics/
  data.py          data loading and validation
  features.py      feature engineering
  train.py         training, evaluation, artifact persistence, MLflow logging
  recommend.py     hotel recommendation logic
  api.py           Flask endpoints
  dashboard.py     Streamlit UI
tests/             basic tests
airflow/dags/      scheduled training DAG
k8s/               Kubernetes deployment/service
Dockerfile         API image
docker-compose.yml local API + dashboard
Jenkinsfile        CI/CD pipeline
```

## Responsible use and production checklist

- Validate data lineage, licenses, and permitted use.
- Never expose personal names or identifiers through APIs/logs.
- Gender prediction is sensitive and should be treated as an academic exercise, not used to infer identity or make decisions about people.
- Add authentication, rate limiting, request-size limits, monitoring, secrets management, and HTTPS before public deployment.
- Check drift, retrain on an explicit schedule, and promote models only after evaluation.
