from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
import torch
import librosa
import io

# Initialize the FastAPI app
app = FastAPI(title="ASR Service")

# Load the ASR pipeline from Hugging Face
# Using a distilled version for efficiency on local machine
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model="distil-whisper/distil-small.en",
    torch_dtype=torch.float16,
    device="cuda:0", # Use "cuda:0" if GPU is available
)

@app.post("/infer")
async def infer(audio_file: UploadFile = File(...)):
    """
    Accepts an audio file and returns the transcribed text.
    """
    # Read the audio file content
    audio_bytes = await audio_file.read()

    # Use librosa to load and resample the audio to the required 16kHz
    audio_array, _ = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)

    # Perform inference
    result = asr_pipeline(
        audio_array,
        chunk_length_s=15,
        batch_size=4,
    )

    return {"text": result["text"]}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}