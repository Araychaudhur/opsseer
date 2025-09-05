# OpsSeer

An SRE-style AI portfolio project that demonstrates a complete, automated incident response pipeline. It features a "toy prod" service, a full monitoring/alerting stack, and an orchestrated timeline enriched by a suite of custom-built, GPU-accelerated AI microservices, all visualized in a real-time web UI.

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
- [x] **M7:** Slack (Notifications) & GitHub Integrations
- [x] **M8:** Evaluation Harness
- [x] **M9:** Polishing for Portfolio & UI
- [x] **M10 (Polish):** Interactive Slack Bot

### Next Steps & Future Enhancements
- [ ] **M11 (New Feature):** Time-Series Forecasting Service
- [ ] **M12 (Polish):** Correlate Firing & Resolved Alerts

---

## M10 — Interactive Slack Bot

To create a "human-in-the-loop" workflow, the system includes an interactive Slack bot. Using Slack's Socket Mode, the bot listens for `@mentions` in a channel. An on-call engineer can directly ask the bot questions (e.g., `@OpsSeer Bot what are the rollback steps?`), and the bot will query the DocQA service to provide an immediate, AI-powered answer within the Slack thread.

## How It Works: The AIOps Pipeline

1.  **Detect**: A `toyprod` service emits metrics to **Prometheus**. When an SLO is breached, an alert fires.
2.  **Route**: The alert is sent to **Alertmanager**, which forwards it to the central **Orchestrator**.
3.  **Enrich**: The Orchestrator creates an incident in a **PostgreSQL** database and queries a suite of AI services through the **AI Gateway**.
4.  **Notify**: The Orchestrator sends notifications to a **Slack** channel and creates an issue in **GitHub**.
5.  **Visualize**: A **Frontend UI** displays the complete incident timeline.

## Final Evaluation Metrics

-   **ASR Service**: Achieved **0% Word Error Rate (WER)**.
-   **DocQA Service**: Achieved **100% Accuracy**.

---
## Demo Scenario

1.  **Start the stack**: `docker compose up -d`
2.  **Trigger an alert**: `curl "http://localhost:8080/chaos?delay_ms=400"`
3.  **Generate traffic**: `for ($i=0; $i -lt 60; $i++) { try { Invoke-WebRequest -UseBasicParsing "http://localhost:8080/orders?count=3" | Out-Null } catch {}; Start-Sleep -Milliseconds 250 }`
4.  **Wait 2-3 minutes**. You will receive a Slack message and a GitHub issue will be created.
5.  **Interact with the bot**: In the Slack channel, ask a question like `@OpsSeer Bot what are the rollback steps?` to get an immediate AI response.