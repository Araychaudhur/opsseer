FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir docker prometheus_client
COPY exporter.py .
EXPOSE 9102
CMD ["python", "exporter.py"]