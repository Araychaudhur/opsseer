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
- [x] **M11 (New Feature):** Time-Series Forecasting Service
- [ ] **M12 (Polish):** Correlate Firing & Resolved Alerts

---
## M11 — Time-Series Forecasting

To make the system proactive, a new **Forecaster** service was added. When a high-latency alert occurs, the orchestrator queries Prometheus for the recent metric history and sends it to this service. The service uses the `amazon/chronos-t5-small` model to predict future values. The orchestrator then analyzes this forecast to issue proactive warnings if a future SLO breach is predicted.

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
2.  **Trigger an alert**: For a proactive forecast, use the sine wave latency mode: `curl "http://localhost:8080/chaos?mode=sine&delay_ms=150"`
3.  **Generate traffic**: `for ($i=0; $i -lt 720; $i++) { try { Invoke-WebRequest -UseBasicParsing "http://localhost:8080/orders?count=3" | Out-Null } catch {}; Start-Sleep -Milliseconds 250 }`
4.  **Wait 2-3 minutes**. You will receive a Slack message and a GitHub issue will be created.
5.  **Get the Incident ID**: Check the orchestrator logs for the new ID: `docker compose logs orchestrator`
6.  **View the Timeline**: Open a browser to `http://localhost:8888`, paste the Incident ID, and click "Fetch Timeline". You will see the full incident unfold with a proactive forecast.