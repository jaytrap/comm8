"""
Pydantic models for API responses.
"""
from typing import Optional
from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    """Response model for file transcription endpoint."""

    transcription: str = Field(..., description="Original transcribed text")
    translation: str = Field(..., description="Translated text")
    audio_url: Optional[str] = Field(None, description="URL to download generated TTS audio")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")

    class Config:
        json_schema_extra = {
            "example": {
                "transcription": "Hello, how are you today?",
                "translation": "Hei, mitä kuuluu tänään?",
                "audio_url": "/api/v1/download-audio?file_path=/app/audio_output/translated_audio_123.wav",
                "source_language": "en",
                "target_language": "fi"
            }
        }


class StreamResponse(BaseModel):
    """Response model for streaming transcription."""

    chunk_id: int = Field(..., description="Sequential chunk identifier")
    transcription: str = Field(..., description="Transcribed text for this chunk")
    translation: str = Field(..., description="Translated text for this chunk")
    is_final: bool = Field(..., description="Whether this is the final chunk")
    confidence: float = Field(0.0, description="Transcription confidence score (0-1)")
    error: Optional[str] = Field(None, description="Error message if processing failed")

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": 1,
                "transcription": "Hello there",
                "translation": "Hei siellä",
                "is_final": False,
                "confidence": 0.95,
                "error": None
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid audio format",
                "detail": "Supported formats: wav, mp3, m4a, flac, ogg",
                "code": "INVALID_FORMAT"
            }
        }