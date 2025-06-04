# Start with a known working base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak \
    espeak-data \
    curl \
    build-essential \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install step by step
COPY requirements.txt .

# Install dependencies one by one to identify issues
RUN pip install --upgrade pip

# Install FastAPI first (should work)
RUN pip install fastapi uvicorn[standard] python-multipart pydantic

# Install ML dependencies (most likely to fail)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install audio processing
RUN pip install openai-whisper

# Install TTS (often problematic)
RUN pip install TTS==0.22.0

# Install translation
RUN pip install argostranslate

# Install remaining small dependencies
RUN pip install aiofiles python-json-logger

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp audio_output logs

# Remove build dependencies
RUN apt-get purge -y build-essential python3-dev && \
    apt-get autoremove -y

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]