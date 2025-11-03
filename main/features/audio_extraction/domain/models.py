from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AudioExtractionJob:
    """
    A pure data model representing the job to be done.
    It has no logic, only data.
    """
    video_file_path: Path
    output_audio_path: Path
    audio_quality_flags: list[str]
