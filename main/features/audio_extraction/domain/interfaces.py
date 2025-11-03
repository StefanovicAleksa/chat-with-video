from abc import ABC, abstractmethod
from .models import AudioExtractionJob

class IAudioExtractor(ABC):
    """
    An abstract interface for an audio extraction tool.
    The domain's use case will depend on this, not on a concrete tool.
    """
    
    @abstractmethod
    def extract(self, job: AudioExtractionJob) -> None:
        """
        Extracts audio according to the job description.
        
        Args:
            job: An AudioExtractionJob model containing all necessary paths
                 and settings for the extraction.
                 
        Raises:
            AudioExtractionError: If the extraction fails for any reason.
        """
        pass
