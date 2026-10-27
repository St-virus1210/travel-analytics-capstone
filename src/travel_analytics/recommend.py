from pathlib import Path
import pandas as pd

def load_recommendation_data(artifact_dir="artifacts", data_dir="data"):
    root = Path(artifact_dir)
    hotels_file, users_file = root / "hotels.pkl", root / "users.pkl"
    hotels = pd.read_pickle(hotels_file) if hotels_file.exists() else pd.read_csv(Path(data_dir) / "hotels.csv")
    users = pd.read_pickle(users_file) if users_file.exists() else pd.read_csv(Path(data_dir) / "users.csv")
    return hotels, users

def recommend_hotels(hotels, user_code=None, place=None, max_price=None, limit=5):
    """Rank hotels by user history, popularity, and optional destination/price constraints."""
    df = hotels.copy()
    if df.empty:
        return []
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["days"] = pd.to_numeric(df["days"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    df = df.dropna(subset=["name", "place", "price"])
    if place:
        matched = df[df["place"].astype(str).str.casefold() == str(place).casefold()]
        if not matched.empty:
            df = matched
        else:
            df = df[df["place"].astype(str).str.contains(str(place), case=False, na=False)]
    if max_price is not None:
        df = df[df["price"] <= float(max_price)]
    if df.empty:
        return []
    stats = df.groupby(["name", "place"], dropna=False).agg(
        avg_price=("price", "mean"), avg_days=("days", "mean"),
        bookings=("travelCode", "count"), avg_total=("total", "mean")
    ).reset_index()
    stats["score"] = stats["bookings"].rank(pct=True) * 0.65 + (1 - stats["avg_price"].rank(pct=True)) * 0.35
    if user_code is not None:
        try:
            uid = int(user_code)
            history = hotels[pd.to_numeric(hotels["userCode"], errors="coerce") == uid]
            if not history.empty:
                preferred_places = set(history["place"].dropna().astype(str))
                preferred_names = set(history["name"].dropna().astype(str))
                stats["score"] += stats["place"].astype(str).isin(preferred_places).astype(float) * 0.25
                stats["score"] += stats["name"].astype(str).isin(preferred_names).astype(float) * 0.35
        except (TypeError, ValueError):
            pass
    stats = stats.sort_values(["score", "bookings"], ascending=False).head(max(1, min(int(limit), 50)))
    return [{
        "hotel": str(row["name"]), "place": str(row["place"]),
        "average_price_per_day": round(float(row["avg_price"]), 2),
        "average_days": round(float(row["avg_days"]), 1) if pd.notna(row["avg_days"]) else None,
        "average_total": round(float(row["avg_total"]), 2) if pd.notna(row["avg_total"]) else None,
        "historical_bookings": int(row["bookings"]), "score": round(float(row["score"]), 4)
    } for _, row in stats.iterrows()]
