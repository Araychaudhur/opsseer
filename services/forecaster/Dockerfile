# Use an official PyTorch image with the full CUDA toolkit
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# The new base image has pip and python, so the rest of the setup is similar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add this line to upgrade torch and torchvision to a compatible version
RUN pip install --upgrade torch==2.3.1 torchvision==0.18.1

COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]