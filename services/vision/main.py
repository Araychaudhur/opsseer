from fastapi import FastAPI, UploadFile, File
import easyocr
import io

app = FastAPI(title="Vision (OCR) Service")

# Load the EasyOCR reader. This will download the model on first run.
# We specify English and tell it to use the GPU.
print("--- Loading EasyOCR Reader (GPU)... ---")
reader = easyocr.Reader(['en'], gpu=True)
print("--- EasyOCR Reader loaded successfully. ---")


@app.post("/infer")
async def infer(image_file: UploadFile = File(...)):
    """
    Accepts an image file and returns the extracted text using EasyOCR.
    """
    image_bytes = await image_file.read()

    # EasyOCR can work with bytes directly
    result = reader.readtext(image_bytes)

    # The result is a list of (bounding_box, text, confidence).
    # We will join all the detected text snippets into a single string.
    extracted_text = " ".join([text for bbox, text, conf in result])

    return {"text": extracted_text}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}