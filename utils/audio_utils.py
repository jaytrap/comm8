import os
import tempfile


def save_audio_file(text, tts_model):
    tts_audio_filename = f"translated_audio_{tempfile.mktemp(suffix='.wav').split('/')[-1]}"
    tts_audio_path = os.path.join(os.getcwd(), tts_audio_filename)
    tts_model.tts_to_file(text, file_path=tts_audio_path)
    return tts_audio_path
