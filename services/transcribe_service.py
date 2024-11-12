import tempfile
from fastapi import UploadFile
from utils.audio_utils import save_audio_file
from utils.translation_utils import translate_text
import whisper
from TTS.api import TTS

tts_model = TTS(model_name="tts_models/fi/css10/vits")

async def process_transcription(file: UploadFile, language: str):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio:
        audio_data = await file.read()
        temp_audio.write(audio_data)
        temp_audio.flush()

        # Transcribe with Whisper
        model = whisper.load_model("base")
        transcribed_audio = model.transcribe(temp_audio.name, fp16=False, language=language)
        transcribed_text = transcribed_audio.get("text")

        # Translate text
        translated_text = translate_text(transcribed_text, "en", "fi")

        # Generate TTS audio file
        audio_file_path = save_audio_file(translated_text, tts_model)

    return {"transcription": transcribed_text, "translation": translated_text, "audio_url": f"/download-audio?file_path={audio_file_path}"}
