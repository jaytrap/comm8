"""
Configuration management for the application.
"""
import os
from pathlib import Path
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    app_name: str = Field(default="Audio Transcription & Translation API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")

    # CORS settings
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")

    # File handling settings
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    temp_dir: str = Field(default="temp", env="TEMP_DIR")
    audio_output_dir: str = Field(default="audio_output", env="AUDIO_OUTPUT_DIR")
    cleanup_interval_hours: int = Field(default=24, env="CLEANUP_INTERVAL_HOURS")

    # Model settings
    whisper_model: str = Field(default="base", env="WHISPER_MODEL")
    tts_model: str = Field(default="tts_models/fi/css10/vits", env="TTS_MODEL")

    # Streaming settings
    stream_chunk_duration: float = Field(default=2.0, env="STREAM_CHUNK_DURATION")
    stream_buffer_size: int = Field(default=32000, env="STREAM_BUFFER_SIZE")  # 16kHz * 2 seconds * 2 bytes

    # Translation settings
    default_source_language: str = Field(default="en", env="DEFAULT_SOURCE_LANGUAGE")
    default_target_language: str = Field(default="fi", env="DEFAULT_TARGET_LANGUAGE")
    max_translation_length: int = Field(default=5000, env="MAX_TRANSLATION_LENGTH")

    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # Security settings
    allowed_audio_formats: List[str] = Field(
        default=[".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"],
        env="ALLOWED_AUDIO_FORMATS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def temp_dir_path(self) -> Path:
        """Get temp directory as Path object."""
        return Path(self.temp_dir)

    @property
    def audio_output_dir_path(self) -> Path:
        """Get audio output directory as Path object."""
        return Path(self.audio_output_dir)

    def create_directories(self):
        """Create necessary directories if they don't exist."""
        self.temp_dir_path.mkdir(exist_ok=True)
        self.audio_output_dir_path.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()

# Create directories on import
settings.create_directories()