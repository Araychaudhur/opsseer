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

### Next Steps & Future Enhancements
- [ ] **M10 (Polish):** Interactive Slack Bot
- [ ] **M11 (New Feature):** Time-Series Forecasting Service
- [ ] **M12 (Polish):** Correlate Firing & Resolved Alerts

---

## How It Works: The AIOps Pipeline

1.  **Detect**: A `toyprod` service emits metrics to **Prometheus**. When an SLO is breached (e.g., high error rate or latency), a pre-configured alert fires.
2.  **Route**: The alert is sent to **Alertmanager**, which forwards it to the central **Orchestrator** service.
3.  **Enrich**: The Orchestrator creates a new incident in a **PostgreSQL** database and queries a suite of AI services through a unified **AI Gateway**:
    -   **DocQA Service** is queried to find relevant steps from Markdown runbooks.
    -   **Vision Service** is triggered on latency alerts to capture a Grafana panel screenshot and perform OCR to extract key text from the image.
    -   **ASR Service** is available for future use with audio inputs.
4.  **Notify**: The Orchestrator takes the initial alert and the AI-generated insights and sends notifications to:
    -   A **Slack** channel for real-time awareness.
    -   A **GitHub** repository by creating a new, trackable issue.
5.  **Visualize**: A simple **Frontend UI** can be used to view the complete, ordered timeline of any incident by querying the Orchestrator's REST API.

## Final Evaluation Metrics

-   **ASR Service**: Achieved **0% Word Error Rate (WER)** on the test set.
-   **DocQA Service**: Achieved **100% Accuracy** on the test set.

---
## Demo Scenario

1.  **Start the stack**: `docker compose up -d`
2.  **Trigger an alert**: For example, a high latency alert: `curl "http://localhost:8080/chaos?delay_ms=400"`
3.  **Generate traffic**: `for ($i=0; $i -lt 60; $i++) { try { Invoke-WebRequest -UseBasicParsing "http://localhost:8080/orders?count=3" | Out-Null } catch {}; Start-Sleep -Milliseconds 250 }`
4.  **Wait 2-3 minutes**. You will receive a Slack message and a GitHub issue will be created.
5.  **Get the Incident ID**: Check the orchestrator logs for the new ID: `docker compose logs orchestrator`
6.  **View the Timeline**: Open a browser to `http://localhost:8888`, paste the Incident ID, and click "Fetch Timeline". You will see the full incident unfold.