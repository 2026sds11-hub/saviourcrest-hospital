# Base image
FROM python:3.10-slim

# Working directory set karein
WORKDIR /app

# Requirements copy karein aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baqi sara code copy karein
COPY . .

# FastAPI ko chalane ki command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]