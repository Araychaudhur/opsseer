import asyncio, os, random, time
from typing import List
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

app = FastAPI(title="toyprod")

# ---- Chaos state (live-tunable) ----
FAIL_RATE = float(os.getenv("FAIL_RATE", "0"))
BASE_DELAY_MS = int(os.getenv("BASE_DELAY_MS", "0"))

# ---- Metrics ----
REQUESTS = Counter(
    "toyprod_requests_total",
    "HTTP requests",
    ["route", "method", "status"],
)
LATENCY = Histogram(
    "toyprod_request_latency_seconds",
    "Request latency (seconds)",
    ["route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)
ORDERS = Counter(
    "toyprod_orders_total",
    "Orders processed (by result)",
    ["result"],  # ok | error
)

# ---- Models ----
class Order(BaseModel):
    id: int
    item: str
    price: float

ITEMS = ["widget", "gizmo", "doodad", "sprocket", "flux-capacitor"]

# ---- Middleware for metrics ----
@app.middleware("http")
async def metrics_middleware(request, call_next):
    route = request.url.path
    method = request.method
    start = time.perf_counter()
    status = "500"
    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response
    finally:
        dur = time.perf_counter() - start
        REQUESTS.labels(route=route, method=method, status=status).inc()
        LATENCY.labels(route=route).observe(dur)

# ---- Endpoints ----
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/orders")
async def get_orders(count: int = 1):
    # latency
    if BASE_DELAY_MS > 0:
        await asyncio.sleep(BASE_DELAY_MS / 1000.0)

    # failure injection per-request (independent of count)
    if FAIL_RATE > 0 and random.random() < FAIL_RATE:
        ORDERS.labels(result="error").inc()
        raise HTTPException(status_code=500, detail="simulated failure")

    # generate orders
    orders: List[Order] = []
    for i in range(count):
        orders.append(Order(
            id=random.randint(1000, 9999),
            item=random.choice(ITEMS),
            price=round(random.uniform(5, 250), 2),
        ))
    ORDERS.labels(result="ok").inc()
    return {"orders": [o.model_dump() for o in orders],
            "delay_ms": BASE_DELAY_MS, "fail_rate": FAIL_RATE}

@app.get("/chaos")
async def chaos(delay_ms: int | None = None, fail_rate: float | None = None):
    global BASE_DELAY_MS, FAIL_RATE
    if delay_ms is not None:
        BASE_DELAY_MS = max(0, int(delay_ms))
    if fail_rate is not None:
        FAIL_RATE = max(0.0, min(1.0, float(fail_rate)))
    return {"delay_ms": BASE_DELAY_MS, "fail_rate": FAIL_RATE}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
