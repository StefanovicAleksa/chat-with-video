# File: main/features/transcription/exceptions/errors.py
"""
Custom exceptions for the transcription feature.
This allows the service layer to catch specific errors from this feature.
"""

class TranscriptionError(Exception):
    """Base exception for all transcription errors."""
    pass

class AudioFileNotFoundError(TranscriptionError):
    """Raised when the input audio file does not exist."""
    pass

class WhisperModelError(TranscriptionError):
    """Raised when the Whisper model itself fails to load (e.g., OOM error)."""
    pass