# File: main/features/transcription/domain/use_case.py
from pathlib import Path
from .interfaces import ITranscriber
from .models import TranscriptionJob, TranscriptionResult
from ..exceptions.errors import AudioFileNotFoundError

class CreateTranscriptionUseCase:
    """
    This is the pure, core business logic for transcription.
    It is completely decoupled from Whisper or any other specific tool.
    """
    
    def __init__(self, transcriber: ITranscriber):
        """
        Initializes the use case by injecting its dependency (the "port").
        
        Args:
            transcriber: Any object that conforms to the ITranscriber interface.
        """
        self._transcriber = transcriber

    def execute(self, audio_path: Path) -> TranscriptionResult:
        """
        Executes the transcription use case.
        
        Args:
            audio_path: The Path object to the input audio file.
        
        Returns:
            A TranscriptionResult model.
            
        Raises:
            AudioFileNotFoundError: If the input audio file does not exist.
            TranscriptionError: If the transcription itself fails.
        """
        # --- Start of pure business logic ---
        
        # 1. Validation
        if not audio_path.exists():
            raise AudioFileNotFoundError(f"Audio file not found at: {audio_path}")
            
        if not audio_path.is_file():
            raise AudioFileNotFoundError(f"Path is not a file: {audio_path}")

        # 2. Create the domain model for the job
        job = TranscriptionJob(
            audio_file_path=audio_path
            # We are using defaults for language (auto-detect) and fp16 (True)
        )

        # 3. Delegate the "dirty" work to the injected transcriber
        # We don't know *how* it works, just that it fulfills the contract.
        result = self._transcriber.transcribe(job)
        
        # 4. Return the pure result model
        return result
        
        # --- End of pure business logic ---