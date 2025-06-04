"""
Input validation utilities.
"""
import logging
from pathlib import Path
from typing import Set

from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_AUDIO_FORMATS: Set[str] = {
    ".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"
}

# Supported language codes
SUPPORTED_LANGUAGES: Set[str] = {
    "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
    "ar", "hi", "fi", "sv", "no", "da", "nl", "pl", "cs", "sk"
}

# Maximum file size (50MB)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


def validate_audio_file(file: UploadFile) -> None:
    """
    Validate uploaded audio file.

    Args:
        file: Uploaded file object

    Raises:
        ValueError: If file validation fails
    """
    if not file:
        raise ValueError("No file provided")

    if not file.filename:
        raise ValueError("Filename is required")

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_AUDIO_FORMATS:
        supported_formats = ", ".join(sorted(SUPPORTED_AUDIO_FORMATS))
        raise ValueError(f"Unsupported audio format '{file_extension}'. Supported formats: {supported_formats}")

    # Check file size
    if hasattr(file, 'size') and file.size:
        if file.size > MAX_FILE_SIZE_BYTES:
            max_size_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
            raise ValueError(
                f"File size ({file.size / (1024 * 1024):.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)")

    # Check content type if available
    if file.content_type and not file.content_type.startswith(('audio/', 'video/')):
        logger.warning(f"Unexpected content type: {file.content_type}")


def validate_language_code(language: str) -> None:
    """
    Validate language code.

    Args:
        language: Language code to validate

    Raises:
        ValueError: If language code is invalid
    """
    if not language:
        raise ValueError("Language code is required")

    if not isinstance(language, str):
        raise ValueError("Language code must be a string")

    language = language.lower().strip()

    if len(language) != 2:
        raise ValueError("Language code must be 2 characters long (ISO 639-1)")

    if language not in SUPPORTED_LANGUAGES:
        supported_langs = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise ValueError(f"Unsupported language code '{language}'. Supported languages: {supported_langs}")


def validate_text_input(text: str, max_length: int = 10000) -> None:
    """
    Validate text input.

    Args:
        text: Text to validate
        max_length: Maximum allowed text length

    Raises:
        ValueError: If text validation fails
    """
    if not text:
        raise ValueError("Text input is required")

    if not isinstance(text, str):
        raise ValueError("Text input must be a string")

    text = text.strip()

    if not text:
        raise ValueError("Text input cannot be empty or whitespace only")

    if len(text) > max_length:
        raise ValueError(f"Text length ({len(text)}) exceeds maximum allowed length ({max_length})")


def validate_file_path(file_path: str, allowed_directories: Set[str] = None) -> None:
    """
    Validate file path for security.

    Args:
        file_path: File path to validate
        allowed_directories: Set of allowed directory names

    Raises:
        ValueError: If file path validation fails
    """
    if not file_path:
        raise ValueError("File path is required")

    if not isinstance(file_path, str):
        raise ValueError("File path must be a string")

    # Convert to Path object for validation
    path = Path(file_path)

    # Check for path traversal attempts
    if ".." in path.parts:
        raise ValueError("Path traversal is not allowed")

    # Check if file exists
    if not path.exists():
        raise ValueError("File does not exist")

    # Check if it's a file (not directory)
    if not path.is_file():
        raise ValueError("Path must point to a file")

    # Validate allowed directories if specified
    if allowed_directories:
        # Check if file is in one of the allowed directories
        resolved_path = path.resolve()
        cwd = Path.cwd()

        is_in_allowed_dir = False
        for allowed_dir in allowed_directories:
            allowed_path = (cwd / allowed_dir).resolve()
            try:
                resolved_path.relative_to(allowed_path)
                is_in_allowed_dir = True
                break
            except ValueError:
                continue

        if not is_in_allowed_dir:
            raise ValueError(f"File must be in one of the allowed directories: {', '.join(allowed_directories)}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"

    # Remove path components
    filename = Path(filename).name

    # Replace potentially dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:250 - len(ext)] + ext

    return filename