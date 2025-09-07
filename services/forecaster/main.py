from fastapi import FastAPI
from pydantic import BaseModel, conlist
import torch
from chronos import ChronosPipeline
from typing import List

app = FastAPI(title="Time-Series Forecasting Service")

# --- Model Loading ---
print("--- Loading Chronos-T5 forecasting pipeline... ---")
pipeline = ChronosPipeline.from_pretrained(
  "amazon/chronos-t5-small",
  device_map="cuda",
  torch_dtype=torch.bfloat16,
)
print("--- Forecasting pipeline loaded successfully. ---")


# --- API Models ---
class ForecastRequest(BaseModel):
    history: conlist(float, min_length=1)
    prediction_length: int = 12

class ForecastResponse(BaseModel):
    forecast: List[float]


# --- API Endpoints ---
@app.post("/forecast")
def forecast_endpoint(request: ForecastRequest):
    """
    Accepts historical time-series data and returns a forecast.
    """
    context = torch.tensor(request.history)

    forecast_tensor = pipeline.predict(
        context,
        request.prediction_length,
        num_samples=1,
    )

    forecast_values = forecast_tensor.squeeze(0).tolist()
    return {"forecast": forecast_values}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}