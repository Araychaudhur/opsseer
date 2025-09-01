# OpsSeer

An SRE-style AI portfolio project with a "toy prod" service, metrics (Prometheus), dashboards (Grafana), chaos & alerting, LLM services (ASR, DocQA, classifier, forecaster), and an orchestrated incident timeline with assets (audio, runbooks, screenshots).

## Milestones

- [x] **M0:** Project Scaffold
- [x] **M1:** ToyProd Service + Core Metrics
- [x] **M2:** SLOs, Alerts & Chaos Scripts
- [x] **M3:** Alertmanager + Grafana Alerting Pipeline
- [x] **M4:** Grafana Image Renderer + Incident Capture
- [x] **M5 (Infrastructure):** Per-Service Container Monitoring
- [ ] **M5 (AI Services):** ML Microservices (ASR, DocQA, etc.)
- [ ] **M6:** Orchestrator + Live Timeline
- [ ] **M7:** Slack & GitHub Integrations
- [ ] **M8:** Evaluation Harness
- [ ] **M9:** Polishing for Portfolio

---

## Milestone M5 — Per-Service Container Monitoring (Resolved)

A key requirement for observing the system during incidents is collecting per-service container metrics (CPU, memory).

The initial approach using **cAdvisor** proved incompatible with the host's Docker environment, failing to detect individual containers correctly. After a thorough debugging process, a more robust architectural solution was implemented:

1.  **cAdvisor was replaced** to eliminate the environmental dependency.
2.  A new, lightweight **`dockerstats` exporter** was created in Python to fetch metrics directly from the Docker socket API.
3.  The existing **`dockermeta` exporter** provides the mapping from container IDs to their Compose service names.
4.  **Prometheus recording rules** now join the data from these two exporters to produce the final `svc:*` metrics for per-service monitoring in Grafana.

This pivot successfully resolved the blocker and established a reliable monitoring foundation for the rest of the project.

---
## Getting Started

**Services**
- `toyprod` (FastAPI): `/healthz`, `/orders?count=N`, `/chaos?delay_ms=&fail_rate=`, `/metrics`
- Prometheus (`:9090`) scrapes all services.
- Grafana (`:3000`) provides dashboards. Default login is `admin`/`admin`.

**Quick start**
```powershell
# Start the full stack
./task.ps1 up

# Generate sample traffic
for ($i=0; $i -lt 60; $i++) { try { Invoke-WebRequest -UseBasicParsing "http://localhost:8000/orders?count=3" | Out-Null } catch {}; Start-Sleep -Milliseconds 250 }

# Trigger a sample incident
Invoke-WebRequest -UseBasicParsing "http://localhost:8000/chaos?delay_ms=200&fail_rate=0.3" | Out-Null