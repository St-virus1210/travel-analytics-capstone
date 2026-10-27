import pytest
pytest.importorskip("flask")
from travel_analytics.api import create_app
def test_health_reports_missing_models(tmp_path):
 c=create_app(model_dir=tmp_path,data_dir=tmp_path).test_client()
 r=c.get("/health"); assert r.status_code==200 and r.get_json()["models_available"] is False
def test_flight_payload_validation(tmp_path):
 c=create_app(model_dir=tmp_path,data_dir=tmp_path).test_client()
 r=c.post("/predict/flight-price",json={"from":"A"}); assert r.status_code==400 and "fields" in r.get_json()
