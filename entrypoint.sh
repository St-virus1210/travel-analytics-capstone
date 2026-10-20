#!/bin/sh
set -eu
if [ ! -f "${MODEL_DIR:-/app/artifacts}/flight_price_model.joblib" ] || [ ! -f "${MODEL_DIR:-/app/artifacts}/gender_classifier.joblib" ]; then
  python -m travel_analytics.train --data-dir "${DATA_DIR:-/app/data}" --artifact-dir "${MODEL_DIR:-/app/artifacts}"
fi
exec "$@"
