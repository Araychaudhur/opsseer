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
- [ ] **M6:** Orchestrator + Live Timeline
- [ ] **M7:** Slack & GitHub Integrations
- [ ] **M8:** Evaluation Harness
- [ ] **M9:** Polishing for Portfolio

---

## M5 — AI Services Stack

A suite of containerized, GPU-accelerated AI microservices has been developed to provide insights during incidents. All services are unified behind a single **AI Gateway**, which simplifies the architecture and routing.

* **ASR (Audio-to-Text) Service**: Transcribes audio files (e.g., from on-call engineer voice notes) into text using a distilled Whisper model.
* **Vision (OCR) Service**: Performs Optical Character Recognition on images (e.g., Grafana dashboard screenshots) to extract text using Microsoft's TrOCR model.
* **DocQA (Document QA) Service**: Answers natural language questions based on a knowledge base of Markdown runbooks using a Retrieval-Augmented Generation (RAG) pipeline.

This completes the core AI inference capabilities of the project.

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