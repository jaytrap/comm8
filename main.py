"""
Main FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.transcribe_controller import router as transcribe_router
from services.model_service import ModelService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    await ModelService.initialize()
    logger.info("Models initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await ModelService.cleanup()
    logger.info("Cleanup completed")


app = FastAPI(
    title="Audio Transcription & Translation API",
    description="API for transcribing audio files and translating text with TTS",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcribe_router, prefix="/api/v1", tags=["transcription"])


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {"message": "Audio Transcription & Translation API", "status": "healthy"}


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": ModelService.is_initialized(),
        "endpoints": [
            "/api/v1/bulk-transcribe",
            "/api/v1/stream-transcribe",
            "/api/v1/download-audio"
        ]
    }