from pydantic import BaseModel

class TranscriptionResponse(BaseModel):
    transcription: str
    translation: str
    audio_url: str