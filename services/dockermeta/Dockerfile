FROM python:3.11-slim
RUN pip install --no-cache-dir docker prometheus_client
WORKDIR /app
COPY exporter.py .
EXPOSE 9101
CMD ["python","exporter.py"]
