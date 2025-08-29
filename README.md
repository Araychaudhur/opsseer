# OpsSeer

An SRE-style AI portfolio project with a "toy prod" service, metrics (Prometheus), dashboards (Grafana), chaos & alerting,
LLM services (ASR, DocQA, classifier, forecaster), and an orchestrated incident timeline with assets (audio, runbooks, screenshots).

## Milestones
M0 scaffold → M1 toyprod+metrics → M2 chaos → M3 alerting → M4 runbooks → M5 AI services → M6 orchestrator → M7 Slack/GitHub → M8 evaluation → M9 polish.
\## Milestone M1 — ToyProd + Metrics

**Services**
- `toyprod` (FastAPI): `/healthz`, `/orders?count=N`, `/chaos?delay_ms=&fail_rate=`, `/metrics`
- Prometheus (9090) scrapes `toyprod:8000`
- Grafana (3000) auto-loads dashboard “ToyProd Service Overview”

**Quick start**
```powershell
./task.ps1 up        # start stack
# traffic
for ($i=0; $i -lt 60; $i++) { try { Invoke-WebRequest -UseBasicParsing "http://localhost:8000/orders?count=3" | Out-Null } catch {}; Start-Sleep -Milliseconds 250 }
# chaos (optional)
Invoke-WebRequest -UseBasicParsing "http://localhost:8000/chaos?delay_ms=200&fail_rate=0.3" | Out-Null
````

**Dashboards**

* Grafana → Dashboards → *ToyProd Service Overview* (RPS, p95 latency, error rate
## Milestone M2 — SLO Alerts + Incident Profile
- Recording rules:
  - `toyprod:error_rate:ratio_5m`
  - `toyprod:p95_latency_seconds:5m`
- Alerts:
  - `ToyProdHighErrorRate` (>10% for 2m)
  - `ToyProdHighLatency` (>300ms p95 for 2m)
- Run incident:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File .\scripts\incident-profile.ps1 -qps 4
````

## Milestone M3 — Alertmanager + Grafana Alerts
- Alertmanager at :9093 routes to a local webhook receiver (`alertlogger`).
- Grafana unified alert "GrafanaErrorRateHigh" notifies the same receiver.
- Verify:
  - Tail logs: `docker compose logs -f alertlogger`
  - Prometheus → Alerts firing produce `/alerts` posts.
  - Grafana Contact Point “AlertLogger” test (or real firing) produces `/grafana` posts.
### Log rotation
Enabled per-service Docker log rotation (local driver). Default limits:
- prometheus/grafana: 10MB × 3 files
- alertmanager/alertlogger/toyprod: 5MB × 3 files

Verify:
```powershell
docker inspect alertlogger --format '{{json .HostConfig.LogConfig}}'
````

Fresh logs for a service:

```powershell
docker compose rm -sf alertlogger
docker compose up -d alertlogger
```

