import os
import time
import httpx
import json
import re
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
GRAFANA_URL = "http://grafana:3000"
PROMETHEUS_URL = "http://prometheus:9090"
LATENCY_SLO = 0.300 # 300ms

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
timeline_table = Table("timeline", metadata, autoload_with=engine)

app = FastAPI(title="Orchestrator")

# (CORS Middleware remains the same)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8888"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # (Startup logic remains the same)
    try:
        with engine.connect() as connection:
            print("--- Database connection verified, timeline table loaded. ---")
    except Exception as e:
        print(f"FATAL: Could not connect to database on startup: {e}")

# (Helper functions add_timeline_event, post_to_slack, create_github_issue, capture_grafana_panel remain the same)
def add_timeline_event(incident_id: str, event_type: str, payload: dict):
    with engine.connect() as connection:
        stmt = insert(timeline_table).values(incident_id=incident_id, type=event_type, payload=payload)
        connection.execute(stmt)
        connection.commit()
    print(f"--- Inserted event '{event_type}' for incident {incident_id} ---")

def post_to_slack(incident_id: str, alert: dict, ai_insight: dict, proactive_warning: str = ""):
    if not SLACK_WEBHOOK_URL: return
    webhook = WebhookClient(SLACK_WEBHOOK_URL)
    summary = alert.get('annotations', {}).get('summary', 'No summary')
    docqa_answer = ai_insight.get('answer', 'No answer found.')
    source = ai_insight.get('source', 'Unknown source')

    blocks=[
        {"type": "header", "text": {"type": "plain_text", "text": f":rotating_light: New Incident: {incident_id}"}},
        {"type": "section", "fields": [{"type": "mrkdwn", "text": f"*Alert*\n{summary}"}]},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*AI Suggested Action*:\n>{docqa_answer}\n\n*Source*: `{source}`"}}
    ]

    if proactive_warning:
        blocks.append({ "type": "section", "text": { "type": "mrkdwn", "text": f"⚠️ *Proactive Warning*:\n>{proactive_warning}" }})

    webhook.send(text=f"New Incident: {summary}", blocks=blocks)
    print("--- Slack notification sent. ---")

def create_github_issue(incident_id: str, alert: dict, ai_insight: dict):
    # ... (code is unchanged)
    if not GITHUB_TOKEN or not GITHUB_REPO: return
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        summary = alert.get('annotations', {}).get('summary', 'No summary')
        description = alert.get('annotations', {}).get('description', 'No description.')
        docqa_answer = ai_insight.get('answer', 'No answer found.')
        source = ai_insight.get('source', 'Unknown source')
        title = f"Incident {incident_id}: {summary}"
        body = f"### 🚨 Alert Details\n**Summary:** {summary}\n**Description:** {description}\n---\n### 🤖 AI Suggested Action\n**Suggestion:** {docqa_answer}\n**Source:** `{source}`"
        repo.create_issue(title=title, body=body.strip(), labels=["incident"])
        print(f"--- Successfully created GitHub issue in {GITHUB_REPO}. ---")
    except Exception as e:
        print(f"--- ERROR: Failed to create GitHub issue: {e} ---")

async def capture_grafana_panel(dashboard_uid: str, panel_id: int):
    # ... (code is unchanged)
    url = f"{GRAFANA_URL}/render/d-solo/{dashboard_uid}/?orgId=1&panelId={panel_id}&width=1000&height=500&tz=UTC"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
        if response.status_code == 200:
            print(f"--- Successfully captured Grafana panel {panel_id} ---")
            return response.content
    except httpx.RequestError as e:
        print(f"--- ERROR: Failed to capture Grafana panel: {e} ---")
    return None

def parse_ocr_text(text: str) -> dict:
    """Uses regex to find meaningful numbers in the OCR output."""
    # This regex looks for a number (integer or float) followed by "ms"
    match = re.search(r"(\d+\.?\d*)\s*ms", text)
    if match:
        value_ms = float(match.group(1))
        return {"metric": "p95_latency", "value": value_ms, "unit": "ms"}
    return {"raw_text": text}

@app.post("/webhook/alert")
async def receive_alert(request: Request):
    alert_payload = await request.json()
    print(f"--- Received Alert Payload ---")
    incident_id = str(uuid.uuid4())

    alert = alert_payload.get('alerts', [{}])[0]
    add_timeline_event(incident_id, "alert", alert)

    # --- AI Enrichment Workflow ---
    alert_name = alert.get('labels', {}).get('alertname', '')

    # Default action for any alert: query DocQA
    question = f"What is the runbook for the {alert_name} alert?"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{AI_GATEWAY_URL}/route/docqa", json={"query": question})

    qa_result = response.json() if response.status_code == 200 else {}
    add_timeline_event(incident_id, "ai_insight_docqa", qa_result)

    # Send a basic notification right away
    post_to_slack(incident_id, alert, qa_result)
    create_github_issue(incident_id, alert, qa_result)

    # Specific actions for different alerts
    if alert_name == 'ToyProdHighLatency':
        print("--- High latency alert detected, triggering Vision and Forecasting workflows ---")

        # Vision Workflow
        image_bytes = await capture_grafana_panel(dashboard_uid="toyprod-main", panel_id=4) # PANEL ID 4 IS THE NEW STAT PANEL
        if image_bytes:
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {'image_file': ('panel.png', image_bytes, 'image/png')}
                response = await client.post(f"{AI_GATEWAY_URL}/route/vision", files=files)
            if response.status_code == 200:
                vision_result = response.json()
                # NEW: Parse the text to make it meaningful
                parsed_vision_result = parse_ocr_text(vision_result.get("text", ""))
                add_timeline_event(incident_id, "ai_insight_vision", parsed_vision_result)

        # Forecasting Workflow
        end_time = int(time.time())
        start_time = end_time - (60 * 60) # 1 hour of history
        prom_query = f'toyprod:p95_latency_seconds:5m'
        prom_url = f"{PROMETHEUS_URL}/api/v1/query_range?query={prom_query}&start={start_time}&end={end_time}&step=60s"
        async with httpx.AsyncClient(timeout=30.0) as client:
            prom_response = await client.get(prom_url)
        if prom_response.status_code == 200:
            results = prom_response.json()['data']['result']
            if results:
                history_values = [float(val[1]) for val in results[0]['values']]
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(f"{AI_GATEWAY_URL}/route/forecaster", json={"history": history_values})
                if response.status_code == 200:
                    forecast_result = response.json()
                    add_timeline_event(incident_id, "ai_insight_forecast", forecast_result)

                    # NEW: Analyze the forecast for proactive warning
                    proactive_warning = ""
                    for i, val in enumerate(forecast_result.get("forecast", [])[0]):
                        if val > LATENCY_SLO:
                            proactive_warning = f"AI predicts latency will breach the {LATENCY_SLO}s SLO in approximately {i+1} minute(s)."
                            break
                    if proactive_warning:
                        add_timeline_event(incident_id, "ai_proactive_warning", {"warning": proactive_warning})
                        # You could send a follow-up Slack message here too

    return {"status": "ok", "incident_id": incident_id}

# (get_timeline and healthz endpoints remain the same)
@app.get("/timeline/{incident_id}")
def get_timeline(incident_id: str):
    # ... code is unchanged ...
    with engine.connect() as connection:
        stmt = select(timeline_table).where(timeline_table.c.incident_id == incident_id).order_by(timeline_table.c.event_ts)
        results = connection.execute(stmt).fetchall()
        return [dict(row._mapping) for row in results]

@app.get("/healthz")
def healthz():
    # ... code is unchanged ...
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "error", "database": "disconnected"}