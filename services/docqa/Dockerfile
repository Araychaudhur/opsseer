FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Install faiss-gpu dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libopenblas-dev libomp-dev curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]