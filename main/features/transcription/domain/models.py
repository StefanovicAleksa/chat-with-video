# File: main/features/transcription/domain/models.py
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class TranscriptionJob:
    """
    A pure data model representing the transcription job to be done.
    It has no logic, only data.
    """
    audio_file_path: Path
    language: str | None = None  # e.g., "en". If None, whisper will auto-detect
    use_fp16: bool = True        # Use half-precision for (much) faster GPU inference

@dataclass(frozen=True)
class TranscriptionResult:
    """
    A pure data model representing the completed transcription.
    We map the 'dirty' whisper dictionary result to this clean object
    to keep our domain decoupled from the tool.
    """
    text: str
    language: str
    segments: list[dict] = field(default_factory=list) # Full segment data (timestamps, etc.)