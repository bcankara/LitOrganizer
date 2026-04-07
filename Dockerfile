# LitOrganizer v2 - Web Interface Docker Image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-tur \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Volumes for persistent data
VOLUME ["/app/pdf", "/app/processed", "/app/logs", "/app/config"]

# Bind to all interfaces inside Docker
ENV LITORGANIZER_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "litorganizer.py", "--web", "--port", "5000"]
