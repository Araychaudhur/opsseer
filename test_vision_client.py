import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# --- Create a dummy image file in memory ---
# Create a blank white image
img = Image.new('RGB', (400, 50), color = (255, 255, 255))
d = ImageDraw.Draw(img)

# Draw text onto the image
try:
    # Use a common system font, fallback to default if not found
    font = ImageFont.truetype("arial.ttf", 20)
except IOError:
    font = ImageFont.load_default()
d.text((10,10), "TESTING OCR SERVICE 123", fill=(0,0,0), font=font)

# Use a BytesIO object to act like a file in memory
mem_file = BytesIO()
img.save(mem_file, 'PNG')
mem_file.seek(0) # Rewind the file to the beginning
# -----------------------------------------

# Define the API endpoint
url = "http://localhost:8002/infer"

# Send the request
print("Sending test image to Vision (OCR) service...")
try:
    response = requests.post(url, files={"image_file": ("test.png", mem_file, "image/png")})

    if response.status_code == 200:
        print("Success! Response from server:")
        print(response.json())
    else:
        print(f"Error: Server responded with status code {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the service at {url}.")
    print("Please ensure the 'vision' container is running.")