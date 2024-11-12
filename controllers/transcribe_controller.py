from fastapi import APIRouter, UploadFile, Query
from fastapi.responses import FileResponse
from services.transcribe_service import process_transcription
from models.response_model import TranscriptionResponse

router = APIRouter()

@router.post("/bulk-transcribe", response_model=TranscriptionResponse)
async def bulk_transcribe(file: UploadFile, language: str = Query("en")):
    result = await process_transcription(file, language)
    return result

@router.get("/download-audio")
async def download_audio(file_path: str):
    return FileResponse(file_path, media_type="audio/wav", filename="translated_audio.wav")