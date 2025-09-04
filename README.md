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
- [x] **M7:** Slack & GitHub Integrations
- [x] **M8:** Evaluation Harness
- [ ] **M9:** Polishing for Portfolio

---

## M8 — Evaluation Harness

To validate the effectiveness of the AI services, a quantitative evaluation harness was built.

-   **ASR Service Evaluation**: Tested against a ground-truth transcript generated via TTS.
    -   **Result**: **0% Word Error Rate (WER)**, a perfect score.
-   **DocQA Service Evaluation**: Tested against a golden dataset of question-answer pairs derived from the runbooks.
    -   **Result**: **100% Accuracy** on the test set.

These results confirm the high quality and reliability of the core AI components.

## M6 & M7 — Orchestration and Integrations

An **Orchestrator** service acts as the central brain, receiving alerts and coordinating calls to the AI Gateway. Upon receiving an alert and an AI-generated insight, it automatically:
1.  Posts a notification to a **Slack** channel.
2.  Creates a trackable issue in a **GitHub** repository.
3.  Records all events to a persistent **PostgreSQL** timeline, accessible via a REST API.

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