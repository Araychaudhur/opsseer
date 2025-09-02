import requests
import numpy as np
import soundfile as sf
from io import BytesIO

# --- Create a dummy audio file in memory ---
samplerate = 16000  # 16kHz
duration = 1.0      # 1 second
frequency = 440.0   # A4 pitch (inaudible as amplitude is 0)

# Generate silent audio
amplitude = 0
t = np.linspace(0., duration, int(samplerate * duration), endpoint=False)
audio_data = amplitude * np.sin(2. * np.pi * frequency * t)

# Use a BytesIO object to act like a file in memory
mem_file = BytesIO()
sf.write(mem_file, audio_data, samplerate, format='WAV')
mem_file.seek(0) # Rewind the file to the beginning
# -----------------------------------------

# Define the API endpoint
url = "http://localhost:8001/infer"

# Send the request
print("Sending test audio to ASR service...")
try:
    response = requests.post(url, files={"audio_file": ("test.wav", mem_file, "audio/wav")})

    if response.status_code == 200:
        print("Success! Response from server:")
        print(response.json())
    else:
        print(f"Error: Server responded with status code {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the service at {url}.")
    print("Please ensure the 'asr' container is running.")