from pathlib import Path
from .interfaces import IAudioExtractor
from .models import AudioExtractionJob
from ..exceptions.errors import VideoFileNotFoundError

class ExtractAudioUseCase:
    """
    This is the pure, core business logic of the feature.
    It is completely decoupled from any specific tools or libraries.
    """
    
    def __init__(self, extractor: IAudioExtractor):
        """
        Initializes the use case by injecting its dependencies (the "ports").
        
        Args:
            extractor: Any object that conforms to the IAudioExtractor interface.
        """
        self._extractor = extractor

    def execute(self, video_path: Path, output_path: Path, quality_flags: list[str]) -> Path:
        """
        Executes the audio extraction use case.
        
        Args:
            video_path: The Path object to the input video file.
            output_path: The Path object for the desired output audio file.
            quality_flags: A list of flags for audio quality (e.g., ["-q:a", "0"]).
            
        Returns:
            The Path to the created audio file.
            
        Raises:
            VideoFileNotFoundError: If the input video file does not exist.
            AudioExtractionError: If the extraction itself fails.
        """
        # --- Start of pure business logic ---
        
        # 1. Validation
        if not video_path.exists():
            raise VideoFileNotFoundError(f"Video file not found at: {video_path}")
            
        if not video_path.is_file():
            raise VideoFileNotFoundError(f"Path is not a file: {video_path}")

        # 2. Create the domain model
        job = AudioExtractionJob(
            video_file_path=video_path,
            output_audio_path=output_path,
            audio_quality_flags=quality_flags
        )

        # 3. Delegate the "dirty" work to the injected extractor
        # We don't know *how* it extracts (ffmpeg, moviepy, etc.),
        # we just know it fulfills the contract.
        self._extractor.extract(job)
        
        # 4. Return the result
        return output_path
        
        # --- End of pure business logic ---
