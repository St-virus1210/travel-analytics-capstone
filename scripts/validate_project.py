"""Validate datasets and report whether trained model artifacts exist."""
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from travel_analytics.data import load_data

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--require-artifacts",action="store_true")
 args=p.parse_args()
 data=load_data(ROOT/"data")
 for name,df in data.items(): print(f"{name}: {len(df):,} rows x {len(df.columns)} columns")
 required=["flight_price_model.joblib","gender_classifier.joblib","hotels.pkl","users.pkl","flight_metrics.json","gender_metrics.json"]
 missing=[n for n in required if not (ROOT/"artifacts"/n).is_file()]
 if missing:
  print("Model artifacts not yet present:",", ".join(missing))
  if args.require_artifacts: raise SystemExit("Run training to generate model artifacts.")
 else:
  print("Flight metrics:",json.loads((ROOT/"artifacts/flight_metrics.json").read_text()))
  print("Gender metrics:",json.loads((ROOT/"artifacts/gender_metrics.json").read_text()).get("metrics",{}))
 print("Kubernetes manifests:",[p.name for p in (ROOT/"k8s").glob("*.yaml")])
 print("Dataset validation completed; this does not deploy external services.")
if __name__=="__main__": main()
