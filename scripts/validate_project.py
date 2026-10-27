import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from travel_analytics.data import load_data
def main():
 d=load_data(ROOT/"data")
 for name,df in d.items(): print(f"{name}: {len(df):,} rows x {len(df.columns)} columns")
 required=["flight_price_model.joblib","gender_classifier.joblib","hotels.pkl","users.pkl","flight_metrics.json","gender_metrics.json"]
 missing=[x for x in required if not (ROOT/"artifacts"/x).is_file()]
 if missing: raise SystemExit(f"Missing artifacts: {missing}. Run training first.")
 print("All required model artifacts and metrics are present.")
 print("Flight metrics:",json.loads((ROOT/"artifacts/flight_metrics.json").read_text()))
 print("Gender metrics:",json.loads((ROOT/"artifacts/gender_metrics.json").read_text()).get("metrics",{}))
 print("Kubernetes manifests:",[p.name for p in (ROOT/"k8s").glob("*.yaml")])
if __name__=="__main__": main()
