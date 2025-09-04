from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
import torch
from PIL import Image
import io

# Initialize the FastAPI app
app = FastAPI(title="Vision (OCR) Service")

# Load the OCR pipeline from Hugging Face
# Using Microsoft's TrOCR (Transformer-based OCR)
ocr_pipeline = pipeline(
    "image-to-text",
    model="microsoft/trocr-base-stage1",
    torch_dtype=torch.float16,
    device="cpu", # Using the GPU
)

@app.post("/infer")
async def infer(image_file: UploadFile = File(...)):
    """
    Accepts an image file and returns the extracted text.
    """
    # Read the image file content
    image_bytes = await image_file.read()

    # Open the image using Pillow
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Perform inference. The model returns a list of dictionaries.
    result = ocr_pipeline(image)

    # Extract the generated text from the first result
    extracted_text = result[0]['generated_text'] if result else ""

    return {"text": extracted_text}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}