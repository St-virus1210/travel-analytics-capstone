.PHONY: install train test api dashboard
install:
	pip install -r requirements.txt
train:
	PYTHONPATH=src python -m travel_analytics.train --data-dir data --artifact-dir artifacts
test:
	PYTHONPATH=src pytest -q
api:
	PYTHONPATH=src MODEL_DIR=artifacts python -m travel_analytics.api
dashboard:
	PYTHONPATH=src streamlit run src/travel_analytics/dashboard.py
