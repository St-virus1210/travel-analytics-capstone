import os
from pathlib import Path
import requests, pandas as pd, streamlit as st, matplotlib.pyplot as plt
st.set_page_config(page_title="Travel Analytics",page_icon="✈️",layout="wide")
st.title("✈️ Travel Analytics & Recommendations")
st.caption("Dataset exploration and API-backed flight price prediction and hotel recommendations.")
DATA=Path(os.getenv("DATA_DIR","data")); API=os.getenv("API_URL","http://localhost:5000")
@st.cache_data
def load(name): return pd.read_csv(DATA/name)
try: flights,hotels,users=load("flights.csv"),load("hotels.csv"),load("users.csv")
except Exception as e: st.error(f"Could not load datasets from {DATA.resolve()}: {e}"); st.stop()
t1,t2,t3=st.tabs(["Overview","Hotel recommendations","Flight price prediction"])
with t1:
 a,b,c=st.columns(3); a.metric("Flight records",f"{len(flights):,}"); b.metric("Hotel bookings",f"{len(hotels):,}"); c.metric("Users",f"{len(users):,}")
 fig,ax=plt.subplots(); flights["price"].clip(upper=flights["price"].quantile(.99)).hist(bins=40,ax=ax); ax.set_title("Flight price distribution (clipped at 99th percentile)"); st.pyplot(fig)
 st.subheader("Most-booked hotel locations"); st.bar_chart(hotels["place"].value_counts().head(10))
with t2:
 user=st.number_input("User code (-1 for popularity only)",min_value=-1,value=0,step=1)
 places=["Any"]+sorted(hotels["place"].dropna().astype(str).unique().tolist()); place=st.selectbox("Destination",places)
 cap=st.number_input("Maximum price per day (0 = no limit)",min_value=0.0,value=0.0,step=25.0); limit=st.slider("Recommendations",1,20,5)
 if st.button("Get recommendations"):
  params={"limit":limit}
  if user>=0: params["user_code"]=int(user)
  if place!="Any": params["place"]=place
  if cap>0: params["max_price"]=cap
  try:
   r=requests.get(f"{API}/recommendations",params=params,timeout=20); r.raise_for_status(); recs=r.json()["recommendations"]
   st.dataframe(pd.DataFrame(recs),use_container_width=True) if recs else st.info("No matches; remove a filter.")
  except requests.RequestException as e: st.error(f"API unavailable: {e}")
with t3:
 origins=sorted(flights["from"].dropna().astype(str).unique()); dests=sorted(flights["to"].dropna().astype(str).unique())
 agencies=sorted(flights["agency"].dropna().astype(str).unique()); types=sorted(flights["flightType"].dropna().astype(str).unique())
 a,b=st.columns(2)
 origin=a.selectbox("Origin",origins); destination=a.selectbox("Destination",dests); kind=a.selectbox("Flight type",types); agency=b.selectbox("Agency",agencies)
 duration=b.number_input("Duration",min_value=0.0,value=float(flights["time"].median())); distance=b.number_input("Distance",min_value=0.0,value=float(flights["distance"].median())); date=b.date_input("Travel date")
 if st.button("Predict flight price"):
  payload={"from":origin,"to":destination,"flightType":kind,"agency":agency,"time":duration,"distance":distance,"date":date.isoformat()}
  try:
   r=requests.post(f"{API}/predict/flight-price",json=payload,timeout=30); r.raise_for_status(); st.success(f"Predicted price: {r.json()['predicted_price']:.2f} source dataset units")
  except requests.RequestException as e: st.error(f"Prediction API unavailable: {e}")
