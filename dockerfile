# Dockerfile caso use airflow
FROM apache/airflow:2.10.2
COPY src/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt