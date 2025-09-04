import requests
from gtts import gTTS
import jiwer
import os

# --- 1. Define Ground Truth and Generate Test Audio ---
ground_truth_text = "High error rate detected in the payments service, please investigate immediately."
audio_filename = "eval_asr_test.mp3"

print(f"--- Generating test audio for sentence: '{ground_truth_text}' ---")
try:
    tts = gTTS(ground_truth_text, lang='en')
    tts.save(audio_filename)
    print(f"Successfully saved test audio to {audio_filename}")
except Exception as e:
    print(f"Failed to generate audio file: {e}")
    exit()

# --- 2. Send Audio to ASR Service via Gateway ---
gateway_url = "http://localhost:8000/route/asr"
print(f"\n--- Sending {audio_filename} to ASR service at {gateway_url} ---")

hypothesis_text = ""
try:
    with open(audio_filename, 'rb') as f:
        response = requests.post(gateway_url, files={"audio_file": (audio_filename, f, "audio/mpeg")})

    if response.status_code == 200:
        hypothesis_text = response.json().get("text", "").strip()
        print(f"Successfully received transcription from model.")
    else:
        print(f"Error: ASR service responded with status code {response.status_code}")
        print(response.text)
        exit()

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the gateway.")
    exit()
finally:
    # Clean up the generated audio file
    if os.path.exists(audio_filename):
        os.remove(audio_filename)

# --- 3. Calculate Word Error Rate (WER) and Print Report ---
if hypothesis_text:
    wer_score = jiwer.wer(ground_truth_text, hypothesis_text)

    print("\n--- ASR Evaluation Report ---")
    print(f"Ground Truth: '{ground_truth_text}'")
    print(f"Hypothesis  : '{hypothesis_text}'")
    print(f"\nWord Error Rate (WER): {wer_score:.2%}")
    print("-----------------------------")
else:
    print("Could not generate a hypothesis to evaluate.")