# OpsSeer

An SRE-style AI portfolio project with a "toy prod" service, metrics (Prometheus), dashboards (Grafana), chaos & alerting, and an orchestrated incident timeline powered by a suite of AI microservices.

## Milestones

- [x] **M0:** Project Scaffold
- [x] **M1:** ToyProd Service + Core Metrics
- [x] **M2:** SLOs, Alerts & Chaos Scripts
- [x] **M3:** Alertmanager + Grafana Alerting Pipeline
- [x] **M4:** Grafana Image Renderer + Incident Capture
- [x] **M5 (Infrastructure):** Per-Service Container Monitoring
- [x] **M5 (AI Services):** Core ML Microservices
- [x] **Bonus:** Unified AI Gateway
- [x] **M6:** Orchestrator + Live Timeline
- [ ] **M7:** Slack & GitHub Integrations
- [ ] **M8:** Evaluation Harness
- [ ] **M9:** Polishing for Portfolio

---

## M6 — Orchestrator & Live Timeline

With the AI services in place, an **Orchestrator** service was created to act as the central brain of the system. Its responsibilities include:

1.  **Receiving Alerts**: It exposes a webhook endpoint that receives firing alerts from Prometheus Alertmanager.
2.  **AI Enrichment**: Upon receiving an alert, it intelligently calls the appropriate AI services via the AI Gateway to get relevant insights (e.g., querying runbooks with the DocQA service).
3.  **Persistent Timeline**: It records all events—the initial alert, the AI-generated insights, and future human actions—into a PostgreSQL database.
4.  **Timeline API**: It exposes a REST API (`GET /timeline/{incident_id}`) to allow other services (like a future frontend or Slack bot) to retrieve the full, ordered history of an incident.

This completes the core automated incident-processing pipeline.

## M5 — AI Services Stack

A suite of containerized, GPU-accelerated AI microservices provides insights during incidents. All services are unified behind a single **AI Gateway**.

* **ASR (Audio-to-Text) Service**: Transcribes audio from voice notes.
* **Vision (OCR) Service**: Extracts text from dashboard screenshots.
* **DocQA (Document QA) Service**: Answers questions based on Markdown runbooks.

---
## Getting Started

**Services**
- `ai-gateway` (`:8000`): The primary entry point for all AI service requests.
- `toyprod` (`:8080`): A sample FastAPI service that can be subjected to chaos engineering.
- Prometheus (`:9090`) & Grafana (`:3000`).

**Quick start**
```powershell
# Start the full stack
./task.ps1 up