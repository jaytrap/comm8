"""
Transcription API controllers.
"""
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Query, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

from services.transcribe_service import TranscribeService
from models.response_model import TranscriptionResponse, StreamResponse
from utils.validators import validate_audio_file, validate_language_code

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/bulk-transcribe", response_model=TranscriptionResponse)
async def bulk_transcribe(
        file: UploadFile = File(..., description="Audio file to transcribe"),
        language: str = Query("en", description="Source language code (e.g., 'en', 'fi', 'es')"),
        target_language: str = Query("fi", description="Target language for translation"),
        generate_audio: bool = Query(True, description="Generate TTS audio for translation")
):
    """
    Transcribe an audio file, translate the text, and optionally generate TTS audio.

    Supported audio formats: wav, mp3, m4a, flac, ogg
    """
    try:
        # Validate inputs
        validate_audio_file(file)
        validate_language_code(language)
        validate_language_code(target_language)

        # Process transcription
        result = await TranscribeService.process_file_transcription(
            file, language, target_language, generate_audio
        )

        logger.info(f"Successfully processed transcription for file: {file.filename}")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing transcription: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during transcription")


@router.websocket("/stream-transcribe")
async def stream_transcribe(
        websocket: WebSocket,
        language: str = Query("en", description="Source language code"),
        target_language: str = Query("fi", description="Target language for translation")
):
    """
    Real-time audio transcription via WebSocket.

    Send audio chunks as binary data and receive transcription results in real-time.
    """
    await websocket.accept()

    try:
        validate_language_code(language)
        validate_language_code(target_language)

        logger.info(f"WebSocket connection established for streaming transcription")

        async for result in TranscribeService.process_stream_transcription(
                websocket, language, target_language
        ):
            await websocket.send_json(result.dict())

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client")
    except ValueError as e:
        logger.error(f"Validation error in stream: {str(e)}")
        await websocket.send_json({"error": str(e)})
        await websocket.close(code=1003)
    except Exception as e:
        logger.error(f"Error in stream transcription: {str(e)}")
        await websocket.send_json({"error": "Internal server error"})
        await websocket.close(code=1011)


@router.get("/download-audio")
async def download_audio(
        file_path: str = Query(..., description="Path to the audio file"),
        filename: Optional[str] = Query(None, description="Custom filename for download")
):
    """
    Download generated TTS audio file.
    """
    try:
        file_path_obj = Path(file_path)

        # Security check: ensure file is in allowed directory
        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Validate file is in the audio output directory
        if not str(file_path_obj.resolve()).startswith(str(Path.cwd() / "audio_output")):
            raise HTTPException(status_code=403, detail="Access denied")

        download_filename = filename or "translated_audio.wav"

        return FileResponse(
            path=file_path,
            media_type="audio/wav",
            filename=download_filename,
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading audio file")


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported language codes for transcription and translation.
    """
    return JSONResponse({
        "transcription_languages": [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar", "hi", "fi"
        ],
        "translation_languages": [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar", "hi", "fi"
        ]
    })