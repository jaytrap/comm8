"""
Enhanced audio processing utilities.
"""
import asyncio
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from services.model_service import ModelService

logger = logging.getLogger(__name__)

# Ensure audio output directory exists
AUDIO_OUTPUT_DIR = Path.cwd() / "audio_output"
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)

TEMP_DIR = Path.cwd() / "temp"
TEMP_DIR.mkdir(exist_ok=True)


class AudioProcessor:
    """Utility class for audio file operations."""

    SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}

    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> str:
        """
        Save uploaded file to temporary location.

        Args:
            file: Uploaded file object

        Returns:
            Path to saved temporary file
        """
        try:
            # Generate unique filename
            file_extension = Path(file.filename or "audio.wav").suffix.lower()
            temp_filename = f"upload_{uuid.uuid4()}{file_extension}"
            temp_path = TEMP_DIR / temp_filename

            # Read and write file data
            content = await file.read()

            with open(temp_path, "wb") as temp_file:
                temp_file.write(content)

            logger.info(f"Saved uploaded file to: {temp_path}")
            return str(temp_path)

        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            raise

    @staticmethod
    async def save_audio_buffer(audio_data: bytes, filename: str) -> str:
        """
        Save audio buffer to temporary file.

        Args:
            audio_data: Raw audio bytes
            filename: Desired filename

        Returns:
            Path to saved file
        """
        try:
            temp_path = TEMP_DIR / filename

            with open(temp_path, "wb") as temp_file:
                temp_file.write(audio_data)

            logger.debug(f"Saved audio buffer to: {temp_path}")
            return str(temp_path)

        except Exception as e:
            logger.error(f"Error saving audio buffer: {str(e)}")
            raise

    @staticmethod
    async def generate_tts_audio(text: str, language: str = "fi") -> str:
        """
        Generate TTS audio file from text.

        Args:
            text: Text to convert to speech
            language: Target language for TTS

        Returns:
            Path to generated audio file
        """
        try:
            # Generate unique filename
            audio_filename = f"tts_{uuid.uuid4()}.wav"
            audio_path = AUDIO_OUTPUT_DIR / audio_filename

            # Generate TTS audio using model service
            await ModelService.generate_tts(text, str(audio_path))

            logger.info(f"Generated TTS audio: {audio_path}")
            return str(audio_path)

        except Exception as e:
            logger.error(f"Error generating TTS audio: {str(e)}")
            raise

    @staticmethod
    def validate_audio_format(filename: str) -> bool:
        """
        Validate if audio file format is supported.

        Args:
            filename: Name of the audio file

        Returns:
            True if format is supported
        """
        file_extension = Path(filename).suffix.lower()
        return file_extension in AudioProcessor.SUPPORTED_FORMATS

    @staticmethod
    async def cleanup_temp_files(max_age_hours: int = 24):
        """
        Clean up old temporary files.

        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            # Clean temp directory
            for file_path in TEMP_DIR.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        logger.debug(f"Cleaned up temp file: {file_path}")

            # Clean audio output directory
            for file_path in AUDIO_OUTPUT_DIR.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        logger.debug(f"Cleaned up audio file: {file_path}")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    @staticmethod
    def get_audio_info(file_path: str) -> dict:
        """
        Get basic audio file information.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with audio file info
        """
        try:
            file_path_obj = Path(file_path)

            return {
                "filename": file_path_obj.name,
                "size_bytes": file_path_obj.stat().st_size,
                "format": file_path_obj.suffix.lower(),
                "exists": file_path_obj.exists()
            }

        except Exception as e:
            logger.error(f"Error getting audio info: {str(e)}")
            return {"error": str(e)}