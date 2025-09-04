import os
import time
import httpx
import json
from fastapi import FastAPI, Request
from sqlalchemy import create_engine, text, insert, select
from sqlalchemy.schema import Table, MetaData
from slack_sdk.webhook import WebhookClient
from github import Github
import uuid

# --- Configuration ---
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "opsseer")
DB_HOST = "postgres"
DB_PORT = "5432"
AI_GATEWAY_URL = "http://ai-gateway:8000"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

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
    with engine.connect() as connection:
        stmt = insert(timeline_table).values(incident_id=incident_id, type=event_type, payload=payload)
        connection.execute(stmt)
        connection.commit()
    print(f"--- Inserted event '{event_type}' for incident {incident_id} ---")

def post_to_slack(incident_id: str, alert: dict, ai_insight: dict):
    # (This function remains the same as before)
    if not SLACK_WEBHOOK_URL:
        print("--- SLACK_WEBHOOK_URL not set, skipping notification. ---")
        return
    webhook = WebhookClient(SLACK_WEBHOOK_URL)
    summary = alert.get('annotations', {}).get('summary', 'No summary')
    docqa_answer = ai_insight.get('answer', 'No answer found.')
    source = ai_insight.get('source', 'Unknown source')
    webhook.send(text=f"New Incident: {summary}", blocks=[{"type": "header", "text": {"type": "plain_text", "text": f":rotating_light: New Incident: {incident_id}"}}, {"type": "section", "fields": [{"type": "mrkdwn", "text": f"*Alert*\n{summary}"}]}, {"type": "section", "text": {"type": "mrkdwn", "text": f"*AI Suggested Action*:\n>{docqa_answer}\n\n*Source*: `{source}`"}}])
    print("--- Slack notification sent. ---")

def create_github_issue(incident_id: str, alert: dict, ai_insight: dict):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("--- GITHUB_TOKEN or GITHUB_REPO not set, skipping issue creation. ---")
        return

    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        summary = alert.get('annotations', {}).get('summary', 'No summary')
        description = alert.get('annotations', {}).get('description', 'No description.')
        docqa_answer = ai_insight.get('answer', 'No answer found.')
        source = ai_insight.get('source', 'Unknown source')

        title = f"Incident {incident_id}: {summary}"
        body = f"""
### 🚨 Alert Details
**Summary:** {summary}
**Description:** {description}
---
### 🤖 AI Suggested Action
**Suggestion:** {docqa_answer}
**Source:** `{source}`
"""
        repo.create_issue(title=title, body=body.strip(), labels=["incident"])
        print(f"--- Successfully created GitHub issue in {GITHUB_REPO}. ---")
    except Exception as e:
        print(f"--- ERROR: Failed to create GitHub issue: {e} ---")


@app.post("/webhook/alert")
async def receive_alert(request: Request):
    alert_payload = await request.json()
    print(f"--- Received Alert Payload ---")
    incident_id = str(uuid.uuid4())

    alert = alert_payload.get('alerts', [{}])[0]
    add_timeline_event(incident_id, "alert", alert)

    alert_summary = alert.get('annotations', {}).get('summary', '')
    if "error rate" in alert_summary.lower():
        question = "What are the rollback steps for a bad deployment?"
        print(f"--- Alert summary '{alert_summary}' triggered DocQA query: '{question}' ---")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{AI_GATEWAY_URL}/route/docqa", json={"query": question})

        if response.status_code == 200:
            qa_result = response.json()
            add_timeline_event(incident_id, "ai_insight_docqa", qa_result)
            post_to_slack(incident_id, alert, qa_result)
            create_github_issue(incident_id, alert, qa_result) # New step
        else:
            error_payload = {"error": "Failed to get response from DocQA", "status_code": response.status_code}
            add_timeline_event(incident_id, "ai_insight_error", error_payload)

    return {"status": "ok", "incident_id": incident_id}

@app.get("/timeline/{incident_id}")
def get_timeline(incident_id: str):
    # (This function remains the same as before)
    with engine.connect() as connection:
        stmt = select(timeline_table).where(timeline_table.c.incident_id == incident_id).order_by(timeline_table.c.event_ts)
        results = connection.execute(stmt).fetchall()
        return [dict(row._mapping) for row in results]

@app.get("/healthz")
def healthz():
    # (This function remains the same as before)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "error", "database": "disconnected"}