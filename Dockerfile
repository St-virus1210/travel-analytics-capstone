FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src MODEL_DIR=/app/artifacts DATA_DIR=/app/data
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY api/ api/
COPY streamlit/ streamlit/
COPY scripts/ scripts/
# Supply data/ CSVs and artifacts/ model files via mounted volumes or include them in the build context.
COPY data/ data/
COPY artifacts/ artifacts/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "travel_analytics.api"]
