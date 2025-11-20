# File: main/features/transcription/domain/interfaces.py
from abc import ABC, abstractmethod
from .models import TranscriptionJob, TranscriptionResult

class ITranscriber(ABC):
    """
    An abstract interface for a transcription tool.
    This is the "Port" our Use Case will depend on.
    
    It defines a contract that any transcription tool must follow.
    """
    
    @abstractmethod
    def transcribe(self, job: TranscriptionJob) -> TranscriptionResult:
        """
        Transcribes an audio file according to the job description.
        
        Args:
            job: A TranscriptionJob model containing all necessary info.
            
        Returns:
            A TranscriptionResult model.
            
        Raises:
            TranscriptionError: If the transcription fails for any reason.
        """
        pass