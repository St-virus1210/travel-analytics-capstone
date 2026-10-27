import pandas as pd
from travel_analytics.features import flight_features,user_features
from travel_analytics.recommend import recommend_hotels
from travel_analytics.data import validate_data
def test_flight_features():
 X=flight_features(pd.DataFrame([{"from":"A","to":"B","flightType":"eco","agency":"X","time":2,"distance":100,"date":"2024-01-01"}]))
 assert X.iloc[0]["date_year"]==2024 and "date_month" in X
def test_user_features_excludes_name_and_id():
 assert list(user_features(pd.DataFrame([{"age":25,"company":"X","name":"Person","code":123}])).columns)==["age","company"]
def test_recommender_returns_expected_shape():
 h=pd.DataFrame([{"travelCode":1,"userCode":7,"name":"A","place":"City","days":2,"price":100,"total":200},{"travelCode":2,"userCode":8,"name":"A","place":"City","days":3,"price":100,"total":300},{"travelCode":3,"userCode":9,"name":"B","place":"City","days":2,"price":200,"total":400}])
 result=recommend_hotels(h,user_code=7,limit=2); assert len(result)==2 and "average_price_per_day" in result[0]
def test_validation_rejects_empty_data():
 d={"flights":pd.DataFrame(columns=["travelCode","userCode","from","to","flightType","price","time","distance","agency","date"]),"hotels":pd.DataFrame(columns=["travelCode","userCode","name","place","days","price","total","date"]),"users":pd.DataFrame(columns=["code","company","name","gender","age"])}
 try: validate_data(d); assert False
 except ValueError: pass
