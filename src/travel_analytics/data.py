from pathlib import Path
import pandas as pd

REQUIRED = {
    "flights": {"travelCode", "userCode", "from", "to", "flightType", "price", "time", "distance", "agency", "date"},
    "hotels": {"travelCode", "userCode", "name", "place", "days", "price", "total", "date"},
    "users": {"code", "company", "name", "gender", "age"},
}

def load_data(data_dir="data"):
    root = Path(data_dir)
    data = {name: pd.read_csv(root / f"{name}.csv") for name in REQUIRED}
    validate_data(data)
    return data

def validate_data(data):
    for name, cols in REQUIRED.items():
        if name not in data:
            raise ValueError(f"Missing dataset: {name}")
        missing_cols = cols - set(data[name].columns)
        if missing_cols:
            raise ValueError(f"{name}.csv missing columns: {sorted(missing_cols)}")
        if data[name].empty:
            raise ValueError(f"{name}.csv contains no rows")
    if (pd.to_numeric(data["flights"]["price"], errors="coerce").dropna() < 0).any():
        raise ValueError("Flight prices must not be negative")
    if (pd.to_numeric(data["hotels"]["total"], errors="coerce").dropna() < 0).any():
        raise ValueError("Hotel totals must not be negative")
    return True
