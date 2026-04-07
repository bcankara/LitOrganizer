# LitOrganizer v2 - Web Interface Docker Image
# Multi-platform: linux/amd64, linux/arm64
FROM python:3.11-slim

# Install system dependencies (OCR + PDF rendering)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-tur \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Keep a pristine copy of the default config so we can seed empty volumes
RUN cp -a /app/config /app/default-config

# Normalize entrypoint line endings (in case of CRLF from Windows checkout)
# and make it executable
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# Persistent data volumes
VOLUME ["/app/pdf", "/app/processed", "/app/logs", "/app/config"]

# Runtime environment
ENV LITORGANIZER_HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:5000/api/status || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "litorganizer.py", "--web", "--port", "5000"]
