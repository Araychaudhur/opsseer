from transformers import pipeline
from PIL import Image
import torch

print("--- Loading Vision (OCR) pipeline on CPU... ---")
try:
    ocr_pipeline = pipeline(
        "image-to-text",
        model="microsoft/trocr-base-stage1",
        device="cpu",
    )
    print("--- Pipeline loaded successfully. ---")

    image_path = "debug_panel.png"
    print(f"--- Opening image: {image_path} ---")
    image = Image.open(image_path).convert("RGB")

    print("--- Attempting to perform OCR... ---")
    result = ocr_pipeline(image)
    print("--- OCR Successful! ---")
    print("Result:", result)

except Exception as e:
    print("\n--- !!! An Error Occurred !!! ---")
    import traceback
    traceback.print_exc()