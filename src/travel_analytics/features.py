import pandas as pd

FLIGHT_CATEGORICAL = ["from", "to", "flightType", "agency"]
FLIGHT_NUMERIC = ["time", "distance", "date_year", "date_month", "date_dayofweek"]
FLIGHT_FEATURES = FLIGHT_CATEGORICAL + FLIGHT_NUMERIC

def flight_features(frame):
    df = frame.copy()
    if "date" not in df:
        df["date"] = "2000-01-01"
    dt = pd.to_datetime(df["date"], errors="coerce")
    df["date_year"] = dt.dt.year.fillna(2000).astype(int)
    df["date_month"] = dt.dt.month.fillna(1).astype(int)
    df["date_dayofweek"] = dt.dt.dayofweek.fillna(0).astype(int)
    for col in FLIGHT_CATEGORICAL:
        if col not in df:
            df[col] = "unknown"
        df[col] = df[col].fillna("unknown").astype(str)
    for col in ["time", "distance"]:
        if col not in df:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return df[FLIGHT_FEATURES]

def user_features(frame):
    df = frame.copy()
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["age"] = df["age"].fillna(df["age"].median())
    df["company"] = df["company"].fillna("unknown").astype(str)
    return df[["age", "company"]]
