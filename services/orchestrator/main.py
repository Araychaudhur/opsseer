import os
import time
import httpx
import json
from fastapi import FastAPI, Request
from sqlalchemy import create_engine, text, insert, select
from sqlalchemy.schema import Table, MetaData
import uuid

# --- Configuration ---
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "opsseer")
DB_HOST = "postgres"
DB_PORT = "5432"
AI_GATEWAY_URL = "http://ai-gateway:8000"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
timeline_table = Table("timeline", metadata, autoload_with=engine)

app = FastAPI(title="Orchestrator")

@app.on_event("startup")
def startup_event():
    try:
        with engine.connect() as connection:
            print("--- Database connection verified, timeline table loaded. ---")
    except Exception as e:
        print(f"FATAL: Could not connect to database on startup: {e}")

def add_timeline_event(incident_id: str, event_type: str, payload: dict):
    """Helper function to insert events into the timeline."""
    with engine.connect() as connection:
        stmt = insert(timeline_table).values(
            incident_id=incident_id,
            type=event_type,
            payload=payload
        )
        connection.execute(stmt)
        connection.commit()
    print(f"--- Inserted event '{event_type}' for incident {incident_id} ---")

@app.post("/webhook/alert")
async def receive_alert(request: Request):
    alert_payload = await request.json()
    print(f"--- Received Alert Payload ---")
    incident_id = str(uuid.uuid4())

    for alert in alert_payload.get('alerts', []):
        add_timeline_event(incident_id, "alert", alert)

    alert_summary = alert_payload.get('commonAnnotations', {}).get('summary', '')
    if "error rate" in alert_summary.lower():
        question = "What are the rollback steps for a bad deployment?"
        print(f"--- Alert summary '{alert_summary}' triggered DocQA query: '{question}' ---")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AI_GATEWAY_URL}/route/docqa",
                json={"query": question}
            )

        if response.status_code == 200:
            qa_result = response.json()
            add_timeline_event(incident_id, "ai_insight_docqa", qa_result)
        else:
            error_payload = {"error": "Failed to get response from DocQA", "status_code": response.status_code}
            add_timeline_event(incident_id, "ai_insight_error", error_payload)

    return {"status": "ok", "incident_id": incident_id}

@app.get("/timeline/{incident_id}")
def get_timeline(incident_id: str):
    """
    Retrieves all events for a given incident_id from the database.
    """
    with engine.connect() as connection:
        stmt = select(timeline_table).where(timeline_table.c.incident_id == incident_id).order_by(timeline_table.c.event_ts)
        results = connection.execute(stmt).fetchall()

        # The result from the DB is a list of tuples, convert it to a list of dicts
        return [dict(row._mapping) for row in results]

@app.get("/healthz")
def healthz():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "error", "database": "disconnected"}