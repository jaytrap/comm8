"""
Transcription service with file and streaming support.
"""
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import UploadFile, WebSocket

from models.response_model import TranscriptionResponse, StreamResponse
from services.model_service import ModelService
from utils.audio_utils import AudioProcessor
from utils.translation_utils import TranslationService

logger = logging.getLogger(__name__)


class TranscribeService:
    """Service for handling audio transcription and translation."""

    @staticmethod
    async def process_file_transcription(
            file: UploadFile,
            source_language: str,
            target_language: str,
            generate_audio: bool = True
    ) -> TranscriptionResponse:
        """
        Process uploaded audio file for transcription and translation.

        Args:
            file: Uploaded audio file
            source_language: Source language code
            target_language: Target language code for translation
            generate_audio: Whether to generate TTS audio

        Returns:
            TranscriptionResponse with results
        """
        temp_file = None

        try:
            # Save uploaded file to temporary location
            temp_file = await AudioProcessor.save_uploaded_file(file)

            # Transcribe audio
            logger.info(f"Transcribing audio file: {file.filename}")
            transcription_result = await ModelService.transcribe_audio(
                temp_file, source_language
            )

            if not transcription_result or not transcription_result.get("text"):
                raise ValueError("Failed to transcribe audio - no text extracted")

            transcribed_text = transcription_result["text"].strip()
            logger.info(f"Transcription completed: {len(transcribed_text)} characters")

            # Translate text if different target language
            translated_text = transcribed_text
            if source_language != target_language:
                logger.info(f"Translating from {source_language} to {target_language}")
                translated_text = await TranslationService.translate_text(
                    transcribed_text, source_language, target_language
                )

            # Generate TTS audio if requested
            audio_url = None
            if generate_audio and translated_text:
                logger.info("Generating TTS audio")
                audio_file_path = await AudioProcessor.generate_tts_audio(
                    translated_text, target_language
                )
                audio_url = f"/api/v1/download-audio?file_path={audio_file_path}"

            return TranscriptionResponse(
                transcription=transcribed_text,
                translation=translated_text,
                audio_url=audio_url,
                source_language=source_language,
                target_language=target_language
            )

        except Exception as e:
            logger.error(f"Error processing file transcription: {str(e)}")
            raise
        finally:
            # Cleanup temporary file
            if temp_file and Path(temp_file).exists():
                Path(temp_file).unlink()

    @staticmethod
    async def process_stream_transcription(
            websocket: WebSocket,
            source_language: str,
            target_language: str,
            chunk_duration: float = 2.0
    ) -> AsyncGenerator[StreamResponse, None]:
        """
        Process streaming audio transcription via WebSocket.

        Args:
            websocket: WebSocket connection
            source_language: Source language code
            target_language: Target language code
            chunk_duration: Duration of audio chunks in seconds

        Yields:
            StreamResponse objects with partial/final results
        """
        audio_buffer = bytearray()
        chunk_counter = 0

        try:
            while True:
                # Receive audio data
                data = await websocket.receive_bytes()
                audio_buffer.extend(data)

                # Process when we have enough data (simple time-based chunking)
                # In production, you might want more sophisticated VAD (Voice Activity Detection)
                if len(audio_buffer) >= 16000 * chunk_duration * 2:  # 16kHz, 16-bit
                    chunk_counter += 1

                    # Create temporary file for this chunk
                    temp_file = None
                    try:
                        temp_file = await AudioProcessor.save_audio_buffer(
                            bytes(audio_buffer), f"stream_chunk_{chunk_counter}.wav"
                        )

                        # Transcribe chunk
                        result = await ModelService.transcribe_audio(
                            temp_file, source_language
                        )

                        if result and result.get("text"):
                            transcribed_text = result["text"].strip()

                            # Translate if needed
                            translated_text = transcribed_text
                            if source_language != target_language:
                                translated_text = await TranslationService.translate_text(
                                    transcribed_text, source_language, target_language
                                )

                            # Yield partial result
                            yield StreamResponse(
                                chunk_id=chunk_counter,
                                transcription=transcribed_text,
                                translation=translated_text,
                                is_final=False,
                                confidence=result.get("confidence", 0.0)
                            )

                        # Clear processed audio from buffer
                        audio_buffer = bytearray()

                    finally:
                        if temp_file and Path(temp_file).exists():
                            Path(temp_file).unlink()

                # Small delay to prevent overwhelming the CPU
                await asyncio.sleep(0.01)

        except Exception as e:
            logger.error(f"Error in stream transcription: {str(e)}")
            # Send final error response
            yield StreamResponse(
                chunk_id=chunk_counter,
                transcription="",
                translation="",
                is_final=True,
                error=str(e)
            )