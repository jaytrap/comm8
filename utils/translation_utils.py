"""
Enhanced translation service utilities.
"""
import asyncio
import logging
from typing import Dict, List, Optional

import argostranslate.package
import argostranslate.translate

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for handling text translation."""

    _packages_installed = False
    _available_languages = None

    @classmethod
    async def initialize(cls):
        """Initialize translation service and install required packages."""
        if cls._packages_installed:
            return

        try:
            logger.info("Initializing translation service...")

            # Update package index
            await asyncio.get_event_loop().run_in_executor(
                None, argostranslate.package.update_package_index
            )

            # Install common language packages
            common_pairs = [
                ("en", "fi"), ("fi", "en"),
                ("en", "es"), ("es", "en"),
                ("en", "fr"), ("fr", "en"),
                ("en", "de"), ("de", "en"),
            ]

            for from_lang, to_lang in common_pairs:
                await cls._install_language_package(from_lang, to_lang)

            cls._packages_installed = True
            logger.info("Translation service initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing translation service: {str(e)}")
            raise

    @classmethod
    async def _install_language_package(cls, from_lang: str, to_lang: str):
        """Install language package if not already installed."""
        try:
            available_packages = argostranslate.package.get_available_packages()

            # Find and install package
            for package in available_packages:
                if package.from_code == from_lang and package.to_code == to_lang:
                    if not package.is_installed():
                        logger.info(f"Installing translation package: {from_lang} -> {to_lang}")
                        await asyncio.get_event_loop().run_in_executor(
                            None, argostranslate.package.install_from_path, package.download()
                        )
                    break

        except Exception as e:
            logger.warning(f"Could not install package {from_lang}->{to_lang}: {str(e)}")

    @classmethod
    async def translate_text(
            cls,
            text: str,
            from_lang: str,
            to_lang: str,
            max_length: int = 5000
    ) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            from_lang: Source language code
            to_lang: Target language code
            max_length: Maximum text length to process

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""

        if from_lang == to_lang:
            return text

        try:
            # Ensure packages are installed
            if not cls._packages_installed:
                await cls.initialize()

            # Truncate text if too long
            if len(text) > max_length:
                logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
                text = text[:max_length]

            # Perform translation in executor to avoid blocking
            translated = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: argostranslate.translate.translate(text, from_lang, to_lang)
            )

            if not translated:
                logger.warning(f"Translation failed for {from_lang}->{to_lang}, returning original text")
                return text

            logger.debug(f"Translated text: {from_lang}->{to_lang} ({len(text)} -> {len(translated)} chars)")
            return translated

        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            # Return original text if translation fails
            return text

    @classmethod
    async def get_available_languages(cls) -> Dict[str, List[str]]:
        """
        Get available language codes for translation.

        Returns:
            Dictionary with 'from' and 'to' language lists
        """
        if cls._available_languages:
            return cls._available_languages

        try:
            installed_packages = argostranslate.package.get_installed_packages()

            from_languages = set()
            to_languages = set()

            for package in installed_packages:
                from_languages.add(package.from_code)
                to_languages.add(package.to_code)

            cls._available_languages = {
                "from": sorted(list(from_languages)),
                "to": sorted(list(to_languages))
            }

            return cls._available_languages

        except Exception as e:
            logger.error(f"Error getting available languages: {str(e)}")
            return {"from": ["en"], "to": ["fi"]}

    @classmethod
    async def batch_translate(
            cls,
            texts: List[str],
            from_lang: str,
            to_lang: str
    ) -> List[str]:
        """
        Translate multiple texts in batch.

        Args:
            texts: List of texts to translate
            from_lang: Source language code
            to_lang: Target language code

        Returns:
            List of translated texts
        """
        if not texts:
            return []

        try:
            # Use asyncio.gather for concurrent translation
            translation_tasks = [
                cls.translate_text(text, from_lang, to_lang)
                for text in texts
            ]

            translated_texts = await asyncio.gather(*translation_tasks)
            return translated_texts

        except Exception as e:
            logger.error(f"Error in batch translation: {str(e)}")
            return texts  # Return original texts if batch translation fails

    @classmethod
    def detect_language(cls, text: str) -> Optional[str]:
        """
        Simple language detection (placeholder - you might want to use a proper library).

        Args:
            text: Text to analyze

        Returns:
            Detected language code or None
        """
        # This is a very basic implementation
        # For production, consider using libraries like langdetect or polyglot

        if not text:
            return None

        # Simple heuristics (extend as needed)
        text_lower = text.lower()

        # Finnish indicators
        finnish_indicators = ["ä", "ö", "y", "koti", "moi", "kiitos", "hei"]
        if any(indicator in text_lower for indicator in finnish_indicators):
            return "fi"

        # Spanish indicators
        spanish_indicators = ["ñ", "¿", "¡", "hola", "gracias", "por favor"]
        if any(indicator in text_lower for indicator in spanish_indicators):
            return "es"

        # Default to English
        return "en"