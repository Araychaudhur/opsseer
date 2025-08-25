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
