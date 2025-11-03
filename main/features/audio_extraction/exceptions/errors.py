"""
Custom exceptions for the audio_extraction feature.
This allows the service layer to catch specific errors from this feature.
"""

class AudioExtractionError(Exception):
    """Base exception for all audio extraction errors."""
    pass

class VideoFileNotFoundError(AudioExtractionError):
    """Raised when the input video file does not exist."""
    pass

class FFmpegExecutionError(AudioExtractionError):
    """Raised when the ffmpeg subprocess fails."""
    pass

class FFmpegBinaryNotFoundError(AudioExtractionError):
    """Raised if the ffmpeg binary is not found in the system's PATH."""
    pass
