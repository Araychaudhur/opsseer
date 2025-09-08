import asyncio, os, random, time, math
from typing import List
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

app = FastAPI(title="toyprod")

# --- Chaos state (live-tunable) ----
CHAOS_MODE = os.getenv("CHAOS_MODE", "none") # none, simple, sine
FAIL_RATE = float(os.getenv("FAIL_RATE", "0"))
BASE_DELAY_MS = int(os.getenv("BASE_DELAY_MS", "0"))
SINE_PERIOD = 600 # 10 minutes for a full wave
SINE_AMPLITUDE = 250 # 250ms variation

# --- Metrics ----
REQUESTS = Counter("toyprod_requests_total", "HTTP requests", ["route", "method", "status"])
LATENCY = Histogram("toyprod_request_latency_seconds", "Request latency (seconds)", ["route"])
ORDERS = Counter("toyprod_orders_total", "Orders processed (by result)", ["result"])

# --- Models ----
class Order(BaseModel):
    id: int
    item: str
    price: float
ITEMS = ["widget", "gizmo", "doodad", "sprocket", "flux-capacitor"]

# --- Middleware for metrics ----
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

# --- Endpoints ----
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/orders")
async def get_orders(count: int = 1):
    # Determine current delay based on chaos mode
    current_delay_ms = 0
    if CHAOS_MODE == "simple":
        current_delay_ms = BASE_DELAY_MS
    elif CHAOS_MODE == "sine":
        # Calculate wave-based delay
        current_time = time.time()
        sine_value = math.sin((2 * math.pi / SINE_PERIOD) * current_time)
        # We want the wave to be all positive, so shift it up
        # It will oscillate between BASE_DELAY_MS and (BASE_DELAY_MS + SINE_AMPLITUDE)
        dynamic_delay = BASE_DELAY_MS + (SINE_AMPLITUDE * (1 + sine_value) / 2)
        current_delay_ms = dynamic_delay

    if current_delay_ms > 0:
        await asyncio.sleep(current_delay_ms / 1000.0)

    if FAIL_RATE > 0 and random.random() < FAIL_RATE:
        ORDERS.labels(result="error").inc()
        raise HTTPException(status_code=500, detail="simulated failure")

    ORDERS.labels(result="ok").inc()
    return {"orders": []} # Return empty list to be quick

@app.get("/chaos")
async def chaos(mode: str = "none", delay_ms: int = 0, fail_rate: float = 0.0):
    global CHAOS_MODE, BASE_DELAY_MS, FAIL_RATE
    CHAOS_MODE = mode
    BASE_DELAY_MS = max(0, int(delay_ms))
    FAIL_RATE = max(0.0, min(1.0, float(fail_rate)))
    return {"mode": CHAOS_MODE, "delay_ms": BASE_DELAY_MS, "fail_rate": FAIL_RATE}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)