# Video Presentation Script — Travel Analytics MLOps Capstone
**Target runtime: 42–45 minutes. Focus: flight-price regression only.**  
**Recording note:** This is a speaking guide, not a pre-recorded video. Record your own screen and narration, use screenshots from your actual runs, and upload the resulting video to your chosen platform. Do not claim a deployment succeeded unless you demonstrate it.

## 00:00–02:30 — Introduction and project objective (2.5 min)
Hello, in this presentation I will explain my travel analytics capstone, focusing only on the flight-price regression workflow from data preparation through deployment and MLOps. The goal is to predict a flight price from characteristics known about the journey and then serve the trained model through a REST API.

The provided flight dataset contains 271,888 rows and 10 columns. It includes travel and user identifiers, origin, destination, flight type, price, duration, distance, agency and date. The hotels and users datasets are part of the wider capstone, but the regression deployment walkthrough will use flights.csv.

The project is not just a model notebook. It is a repeatable pipeline. I will explain data validation, feature engineering, training and evaluation, artifact persistence, MLflow experiment tracking, the Flask API, Streamlit interface, Docker containerization, Kubernetes scaling, Airflow scheduling, Jenkins CI/CD and monitoring.

[SCREEN: Show repository root and README. Point to the single repository URL that will be used in all submission material.]

## 02:30–06:00 — Dataset understanding and validation (3.5 min)
Start by explaining why we inspect the dataset before modeling. We check the shape, column names, data types, missing values, duplicate rows and basic distributions. The target is `price`. A model cannot be trusted if the target is parsed as text, if date values are inconsistent, or if missing values are handled differently between training and inference.

Show the schema and summary statistics. Explain that `travelCode` and `userCode` are identifiers. They are not included as model inputs because they may allow memorization rather than learning generalizable relationships about the journey. Explain that the source data does not explicitly identify the currency, so predictions are reported in the same units as the source price column.

Discuss the difference between a random split and a time-based split. A random split is a useful baseline, but future price prediction should ultimately be evaluated chronologically so that the model does not learn from records later than the examples it predicts.

[SCREEN: Show data shape, missing-value scan and price distribution. Only show actual output from your own notebook.]

## 06:00–11:00 — Exploratory data analysis and feature engineering (5 min)
The next step is exploratory analysis. Examine the price distribution, common origins and destinations, flight types, agencies, duration and distance. Explain that visualizations can reveal skew, outliers, unusual values and category imbalance. If the price distribution has extreme values, do not automatically delete them: first determine whether they are data errors or valid expensive journeys.

Describe the feature set. Categorical features include origin, destination, flight type and agency. Numeric features include duration and distance. The date is converted into year, month and day of week, which can represent broad temporal patterns. The exact useful date features depend on the business question and what information is available at prediction time.

Explain why preprocessing belongs inside a scikit-learn Pipeline. The categorical pipeline fills missing categories and one-hot encodes them. `handle_unknown='ignore'` allows the model to accept a category not observed during training rather than crashing. The numeric pipeline imputes missing values using a training-set median and scales numeric values. A pipeline prevents train/test preprocessing leakage and ensures the same transformations are applied to incoming API requests.

[SCREEN: Show the feature columns and the preprocessing Pipeline code.]

## 11:00–16:00 — Model training and evaluation (5 min)
Explain the baseline-first strategy. Ridge regression provides a regularized linear benchmark. It is relatively simple and helps us understand whether a linear relationship explains a meaningful amount of price variation. The random forest can capture nonlinear interactions among route, distance, duration, agency and flight type, but it is more computationally expensive and can still overfit.

We split the available labeled records into training and test sets. The test set is held out from model fitting and is used for the first estimate of generalization. The candidates are evaluated with MAE, RMSE and R-squared. MAE measures average absolute error in price units. RMSE also measures error in price units but penalizes large misses more heavily. R-squared compares the model with a mean-target baseline, although a negative R-squared is possible when predictions are poor.

Show the actual metric table from your run. State which candidate achieved the lowest MAE and why the selected model is not automatically the most complex model. Do not read invented metric values. If the run has not completed, finish the run before recording.

Discuss residual analysis. Plot predicted values against residuals and look for patterns, changing variance, clusters and large outliers. If errors are much larger for certain routes or high-priced flights, the aggregate MAE may hide an operational weakness. Explain that the next iteration could use chronological validation, route-level metrics, hyperparameter tuning and comparison with gradient boosting.

[SCREEN: Show candidate metric table and residual plot. Zoom in on the measured metrics.]

## 16:00–19:00 — Saving and versioning the model (3 min)
After selecting a candidate, save the entire fitted Pipeline using joblib. This artifact includes the preprocessing and model steps, not just the estimator. This is important because the API must create features in the same way as the training pipeline.

Explain the difference between a model artifact and experiment tracking. The artifact is the object required for inference. Experiment tracking records how it was created, which parameters and metrics were measured, and which run produced it. A joblib file by itself does not fully document the experiment.

Discuss reproducibility: use a fixed random seed where appropriate, pin dependency ranges, validate the schema, and attach an artifact to a particular commit or release. Avoid overwriting a production model without a comparison and promotion process.

[SCREEN: Show the saved flight_price_model.joblib and metrics JSON in the artifacts directory.]

## 19:00–22:30 — MLflow tracking (3.5 min)
MLflow records experiments and runs. The training script creates a named experiment and records candidate model names, the test split, MAE, RMSE and R-squared. It also logs the fitted scikit-learn model artifact. This creates a traceable comparison between the Ridge and random forest candidates.

Open the MLflow UI and select the experiment. Compare the runs side by side. Explain that the metrics table provides evidence for the chosen model. Select a run to show parameters, metrics and artifact files.

Mention the distinction between a local MLflow tracking directory and a shared production tracking server. A local directory is sufficient for a capstone demonstration, but a team deployment should use durable storage, access controls and a clear model registry/promotion workflow. A production system should not rely on a developer laptop as the only copy of experiment history.

[SCREEN: Show MLflow experiment, runs and metrics. Use your actual MLflow UI.]

## 22:30–27:00 — Flask REST API (4.5 min)
The Flask service makes the regression model usable by other applications. It exposes a health endpoint and a flight-price prediction endpoint. The health endpoint helps a caller verify that the API process is responding. The prediction endpoint accepts a JSON object with origin, destination, flight type, duration, distance, agency and date.

Explain request validation. If required fields are absent or the request body is not valid JSON, the service returns a client error. The endpoint applies feature engineering, loads the serialized pipeline, obtains a numeric prediction and returns JSON. Because the source currency is unknown, the response labels the value as dataset units.

Demonstrate a health request, then a successful POST request using Postman or curl. Explain HTTP status codes at a high level: success indicates the request was processed; a client error usually means the input is malformed; a service-unavailable response can indicate that model artifacts are missing. Never expose stack traces, secrets or personal data in public API responses.

For production, add authentication, rate limiting, request-size limits, HTTPS, structured logging, monitoring and a controlled artifact loading strategy. The sample is a teaching implementation, not a fully secured public service.

[SCREEN: Show successful /health response and a real /predict/flight-price request/response.]

## 27:00–30:00 — Streamlit interface (3 min)
Streamlit provides a simple interface for exploring the data and testing predictions. The dashboard shows dataset counts and descriptive charts, then collects route attributes in a form. When the user presses the prediction button, Streamlit sends a request to the Flask API and displays the returned price.

Emphasize the separation of responsibilities. Streamlit handles user interaction and visualization. Flask handles prediction requests. The model artifact is loaded by the API. This separation means the user interface can change without rewriting model logic, and the API can later serve other clients.

Show a complete prediction from form entry to response. Explain that the dashboard does not query live airline inventory and cannot promise an actual bookable fare. It is a prediction based on historical data.

[SCREEN: Show dashboard overview, complete input form and prediction result.]

## 30:00–33:30 — Docker containerization (3.5 min)
Docker packages the Python runtime, dependencies, source code and data into an image. The benefit is a more consistent runtime across a developer environment, a CI agent and a deployment host. The Dockerfile specifies the base Python image, copies requirements, installs dependencies and copies application files.

Explain the distinction between an image and a container. The image is the packaged template; a running container is an instance of that image. Docker Compose starts the API and Streamlit services and places them on a shared network. The dashboard calls the API by its Compose service name.

Run `docker compose up --build` and inspect the containers. Explain the model-artifact strategy. The sample entrypoint trains models if the artifact files are absent, which is convenient for a demonstration but can make startup slow. For production, build and evaluate models in a controlled pipeline, store immutable artifacts, and deploy an image with a known model version. Do not place credentials inside an image.

[SCREEN: Show Docker build output, running containers and a successful health check.]

## 33:30–36:30 — Kubernetes deployment and scaling (3 min)
Kubernetes manages the desired state of containerized services. The included manifest declares two API replicas, a Service, health probes, resource requests and limits, and persistent storage for model artifacts. A Deployment replaces failed Pods and keeps the desired replica count. A Service provides a stable network address even when individual Pods are replaced.

Show the YAML and explain the readiness probe versus liveness probe. Readiness indicates whether a Pod should receive traffic; liveness helps detect a stuck process. Resource requests help the scheduler place workloads, while limits constrain resource consumption.

Explain how to apply the manifest and inspect Pods and Services. The sample manifest is a template: the image must be available to the cluster, and persistent volume support must match the environment. For larger workloads, a HorizontalPodAutoscaler can adjust replicas based on resource metrics. Real deployment also needs ingress/TLS, secrets, monitoring, image registry access and a rollback strategy.

[SCREEN: Show Deployment YAML and actual `kubectl get pods,svc` output if a cluster is available. If not, label the section as configuration review rather than claiming deployment.]

## 36:30–39:00 — Airflow scheduling (2.5 min)
Apache Airflow orchestrates scheduled workflows through a Directed Acyclic Graph. The sample DAG runs the model training command weekly. In an Airflow deployment, the worker needs access to the repository, data files, Python dependencies and a writable artifact location.

Show the DAG graph and the task logs. Explain that scheduling turns manual retraining into a repeatable process, but a schedule alone does not guarantee a safe model release. A more mature DAG separates validation, training, evaluation, quality gates, artifact registration and deployment. If evaluation fails, the pipeline should stop before replacing a production model.

[SCREEN: Show DAG graph and a successful task run from your actual Airflow environment.]

## 39:00–41:30 — Jenkins CI/CD pipeline (2.5 min)
Jenkins automates repeatable checks when code changes. The provided Jenkinsfile checks out the repository, installs dependencies, runs tests, trains and evaluates models, and builds a Docker image. An optional push stage is gated by registry configuration and credentials.

Walk through the stage view and explain why tests come before deployment. If a test fails, the pipeline should stop instead of publishing an unverified build. Registry credentials should be stored in Jenkins credentials, never committed in source code. Production deployment should be a separately configured stage with environment-specific permissions and possibly a manual approval.

[SCREEN: Show a real Jenkins stage view and console output. If Jenkins has not been configured, explain the Jenkinsfile stages without presenting them as a completed run.]

## 41:30–43:30 — Monitoring, retraining and conclusion (2 min)
After deployment, monitor service health, latency, error rates, request volume, input distributions and prediction distributions. When actual prices later become available, calculate delayed prediction errors and compare them with the original validation metrics. Drift can indicate changes in routes, agencies, seasonality or pricing behavior.

Retraining should be triggered by a schedule or an observed need, but a new model should only be promoted after it passes validation and improves on a defined baseline. Keep a record of model version, training data window, code commit and metrics so that the release is traceable and reversible.

To conclude, this project connects model development with an API, user interface, container runtime, orchestrator, scheduled training, CI/CD and experiment tracking. The key lesson is that reliable machine learning depends not only on an algorithm but also on data validation, consistent preprocessing, measurable evaluation, reproducible artifacts and safe deployment practices. Thank you.
