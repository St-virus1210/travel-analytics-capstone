"""Train flight-price regression and recorded-label classification models."""
import argparse, json, os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, balanced_accuracy_score, f1_score, classification_report
from travel_analytics.data import load_data
from travel_analytics.features import FLIGHT_CATEGORICAL, FLIGHT_NUMERIC, flight_features, user_features

try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    mlflow = None
    MLFLOW_AVAILABLE = False

def build_flight_pipeline(model_name="random_forest"):
    prep = ColumnTransformer([
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=2))]), FLIGHT_CATEGORICAL),
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), FLIGHT_NUMERIC),
    ])
    model = RandomForestRegressor(n_estimators=80, min_samples_leaf=2, max_depth=24, random_state=42, n_jobs=-1) if model_name == "random_forest" else Ridge(alpha=2.0)
    return Pipeline([("preprocess", prep), ("model", model)])

def build_gender_pipeline():
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["company"]),
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), ["age"]),
    ])
    return Pipeline([("preprocess", prep), ("model", LogisticRegression(max_iter=1500, class_weight="balanced"))])

def train(data_dir="data", artifact_dir="artifacts"):
    data = load_data(data_dir)
    out = Path(artifact_dir); out.mkdir(parents=True, exist_ok=True)
    if MLFLOW_AVAILABLE: mlflow.set_experiment("travel-analytics-capstone")
    flights = data["flights"].copy()
    cap = int(os.getenv("MAX_FLIGHT_ROWS", "50000"))
    if cap > 0 and len(flights) > cap: flights = flights.sample(n=cap, random_state=42)
    flights["price"] = pd.to_numeric(flights["price"], errors="coerce")
    flights = flights.dropna(subset=["price"])
    X, y = flight_features(flights), flights["price"].astype(float)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
    metrics, best, best_name, best_mae = {}, None, None, float("inf")
    for name in ("ridge", "random_forest"):
        model = build_flight_pipeline(name)
        if MLFLOW_AVAILABLE:
            run_context = mlflow.start_run(run_name=f"flight-regression-{name}")
        else:
            from contextlib import nullcontext
            run_context = nullcontext()
        with run_context:
            model.fit(Xtr, ytr); pred = model.predict(Xte)
            m = {"mae": float(mean_absolute_error(yte, pred)), "rmse": float(np.sqrt(mean_squared_error(yte, pred))), "r2": float(r2_score(yte, pred))}
            metrics[name] = m
            if MLFLOW_AVAILABLE:
                mlflow.log_param("model", name); mlflow.log_param("training_rows", len(Xtr)); mlflow.log_param("test_rows", len(Xte)); mlflow.log_metrics(m)
                mlflow.sklearn.log_model(model, artifact_path="model")
            if m["mae"] < best_mae: best_mae, best, best_name = m["mae"], model, name
    joblib.dump(best, out / "flight_price_model.joblib")
    (out / "flight_metrics.json").write_text(json.dumps({"candidate_metrics":metrics,"selection_metric":"mae","selected_model":best_name}, indent=2))
    users = data["users"].dropna(subset=["gender"]).copy()
    users["gender"] = users["gender"].astype(str)
    ux, uy = user_features(users), users["gender"]
    if uy.nunique() < 2: raise ValueError("Gender classification requires at least two target classes")
    stratify = uy if uy.value_counts().min() >= 2 else None
    uxtr, uxte, uytr, uyte = train_test_split(ux, uy, test_size=.25, random_state=42, stratify=stratify)
    clf = build_gender_pipeline()
    if MLFLOW_AVAILABLE: run_context = mlflow.start_run(run_name="recorded-gender-classification")
    else:
        from contextlib import nullcontext
        run_context = nullcontext()
    with run_context:
        clf.fit(uxtr, uytr); yp = clf.predict(uxte)
        gm = {"accuracy":float(accuracy_score(uyte,yp)),"balanced_accuracy":float(balanced_accuracy_score(uyte,yp)),"macro_f1":float(f1_score(uyte,yp,average="macro",zero_division=0))}
        if MLFLOW_AVAILABLE:
            mlflow.log_param("model","logistic_regression"); mlflow.log_metrics(gm)
            mlflow.log_text(classification_report(uyte,yp,zero_division=0),"classification_report.txt")
            mlflow.sklearn.log_model(clf, artifact_path="model")
    joblib.dump(clf, out / "gender_classifier.joblib")
    (out / "gender_metrics.json").write_text(json.dumps({"metrics":gm,"classification_report":classification_report(uyte,yp,zero_division=0)},indent=2))
    for name in ("hotels","users"): data[name].to_pickle(out / f"{name}.pkl")
    result={"flight_regression":metrics,"gender_classification":gm}
    print(json.dumps(result,indent=2)); return result

def main():
    p=argparse.ArgumentParser(); p.add_argument("--data-dir",default="data"); p.add_argument("--artifact-dir",default="artifacts")
    a=p.parse_args(); train(a.data_dir,a.artifact_dir)
if __name__ == "__main__": main()
