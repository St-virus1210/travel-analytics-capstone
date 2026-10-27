"""Executable Flask application entry point."""
import os
from travel_analytics.api import create_app
app=create_app()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
