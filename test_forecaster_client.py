import requests
import json
import numpy as np

# Define the GATEWAY endpoint for the forecaster service
url = "http://localhost:8000/route/forecaster"

# Generate a sample sine wave as our historical data
t = np.linspace(0, 100, 100)
history_data = np.sin(t * 0.1).tolist()

# Create the request payload
payload = {
    "history": history_data,
    "prediction_length": 24 # Ask for 24 steps into the future
}

print("Sending sample time-series data to Forecaster service...")
try:
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        forecast = result.get("forecast", [])
        print("Success! Response from server:")
        print(f"  -> Forecasted {len(forecast)} steps into the future.")
        print(f"  -> First 5 values: {[round(x, 2) for x in forecast[0][:5]]}")
    else:
        print(f"Error: Server responded with status code {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the gateway at {url}.")