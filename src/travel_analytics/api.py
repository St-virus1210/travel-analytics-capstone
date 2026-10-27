"""Flask API endpoints for prediction and recommendations."""
import os
from pathlib import Path
import joblib, pandas as pd
from flask import Flask, jsonify, request
from travel_analytics.features import flight_features, user_features
from travel_analytics.recommend import load_recommendation_data, recommend_hotels

def create_app(model_dir=None, data_dir=None):
    app=Flask(__name__); model_dir=Path(model_dir or os.getenv("MODEL_DIR","artifacts")); data_dir=data_dir or os.getenv("DATA_DIR","data")
    def model(name):
        path=model_dir/name
        if not path.exists(): raise FileNotFoundError(f"Model artifact missing: {path}; run training first")
        return joblib.load(path)
    @app.get("/health")
    def health(): return jsonify({"status":"ok","models_available":(model_dir/"flight_price_model.joblib").exists() and (model_dir/"gender_classifier.joblib").exists()})
    @app.post("/predict/flight-price")
    def flight_price():
        body=request.get_json(silent=True)
        if not isinstance(body,dict): return jsonify({"error":"Request body must be a JSON object"}),400
        required=["from","to","flightType","time","distance","agency","date"]; missing=[k for k in required if k not in body]
        if missing: return jsonify({"error":"Missing required fields","fields":missing}),400
        try: return jsonify({"predicted_price":round(float(model("flight_price_model.joblib").predict(flight_features(pd.DataFrame([body])))[0]),2),"currency":"dataset_units","note":"Currency is not specified in the source dataset."})
        except FileNotFoundError as e: return jsonify({"error":str(e)}),503
        except (ValueError,TypeError) as e: return jsonify({"error":str(e)}),400
    @app.post("/predict/gender")
    def gender():
        body=request.get_json(silent=True)
        if not isinstance(body,dict) or "age" not in body or "company" not in body: return jsonify({"error":"Required JSON fields: age, company"}),400
        try:
            clf=model("gender_classifier.joblib"); X=user_features(pd.DataFrame([body])); label=str(clf.predict(X)[0])
            probs={str(k):round(float(v),4) for k,v in zip(clf.classes_,clf.predict_proba(X)[0])} if hasattr(clf,"predict_proba") else {}
            return jsonify({"predicted_recorded_gender":label,"class_probabilities":probs,"warning":"Sensitive attribute inference; academic demonstration only, not for decisions about people."})
        except FileNotFoundError as e: return jsonify({"error":str(e)}),503
    @app.get("/recommendations")
    def recommendations():
        try:
            hotels,_=load_recommendation_data(model_dir,data_dir)
            result=recommend_hotels(hotels,user_code=request.args.get("user_code"),place=request.args.get("place"),max_price=request.args.get("max_price",type=float),limit=request.args.get("limit",default=5,type=int))
            return jsonify({"recommendations":result,"count":len(result)})
        except (ValueError,TypeError) as e: return jsonify({"error":str(e)}),400
    return app

app=create_app()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
