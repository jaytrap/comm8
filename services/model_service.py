"""
Centralized model management service.
"""
import asyncio
import logging
from typing import Dict, Optional, Any

import whisper
from TTS.api import TTS

logger = logging.getLogger(__name__)


class ModelService:
    """Singleton service for managing ML models."""

    _instance = None
    _whisper_model = None
    _tts_model = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(cls):
        """Initialize all models asynchronously."""
        if cls._initialized:
            return

        logger.info("Initializing models...")

        try:
            # Initialize Whisper model
            logger.info("Loading Whisper model...")
            cls._whisper_model = await asyncio.get_event_loop().run_in_executor(
                None, whisper.load_model, "base"
            )
            logger.info("Whisper model loaded successfully")

            # Initialize TTS model
            logger.info("Loading TTS model...")
            cls._tts_model = await asyncio.get_event_loop().run_in_executor(
                None, TTS, "tts_models/fi/css10/vits"
            )
            logger.info("TTS model loaded successfully")

            cls._initialized = True
            logger.info("All models initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise

    @classmethod
    async def cleanup(cls):
        """Cleanup models and free memory."""
        logger.info("Cleaning up models...")
        cls._whisper_model = None
        cls._tts_model = None
        cls._initialized = False
        logger.info("Models cleanup completed")

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if models are initialized."""
        return cls._initialized

    @classmethod
    async def transcribe_audio(
            cls,
            audio_path: str,
            language: str = "en",
            **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio file using Whisper.

        Args:
            audio_path: Path to audio file
            language: Language code for transcription
            **kwargs: Additional Whisper parameters

        Returns:
            Transcription result dictionary
        """
        if not cls._initialized or not cls._whisper_model:
            raise RuntimeError("Whisper model not initialized")

        try:
            # Run transcription in executor to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: cls._whisper_model.transcribe(
                    audio_path,
                    language=language,
                    fp16=False,
                    **kwargs
                )
            )
            return result

        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise

    @classmethod
    async def generate_tts(
            cls,
            text: str,
            output_path: str,
            **kwargs
    ) -> str:
        """
        Generate TTS audio from text.

        Args:
            text: Text to convert to speech
            output_path: Output file path
            **kwargs: Additional TTS parameters

        Returns:
            Path to generated audio file
        """
        if not cls._initialized or not cls._tts_model:
            raise RuntimeError("TTS model not initialized")

        try:
            # Run TTS generation in executor
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: cls._tts_model.tts_to_file(
                    text,
                    file_path=output_path,
                    **kwargs
                )
            )
            return output_path

        except Exception as e:
            logger.error(f"Error generating TTS audio: {str(e)}")
            raise

    @classmethod
    def get_whisper_model(cls):
        """Get the Whisper model instance."""
        if not cls._initialized:
            raise RuntimeError("Models not initialized")
        return cls._whisper_model

    @classmethod
    def get_tts_model(cls):
        """Get the TTS model instance."""
        if not cls._initialized:
            raise RuntimeError("Models not initialized")
        return cls._tts_model