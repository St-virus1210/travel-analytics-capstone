"""Smoke-test a running API after training."""
import os, requests
BASE_URL=os.getenv("API_URL","http://127.0.0.1:5000").rstrip("/")
r=requests.get(f"{BASE_URL}/health",timeout=10); r.raise_for_status(); print("GET /health:",r.json())
if not r.json().get("models_available"): raise SystemExit("Models missing; run training first.")
payload={"from":"Recife (PE)","to":"Florianopolis (SC)","flightType":"firstClass","time":1.76,"distance":676.53,"agency":"FlyingDrops","date":"2019-09-26"}
r=requests.post(f"{BASE_URL}/predict/flight-price",json=payload,timeout=30); r.raise_for_status(); print("POST /predict/flight-price:",r.json())
r=requests.get(f"{BASE_URL}/recommendations",params={"limit":5},timeout=20); r.raise_for_status(); print("GET /recommendations:",r.json())
