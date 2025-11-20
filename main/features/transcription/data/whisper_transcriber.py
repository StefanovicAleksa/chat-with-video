# canvas: transcription_data_whisper_transcriber_v2
#
# File: main/features/transcription/data/whisper_transcriber.py
"""
This is the "Adapter" or "Infrastructure" layer.
This file is the ONLY file in the entire feature that
is allowed to `import whisper`.
It implements the ITranscriber interface.
"""
import logging
import whisper # <- The "dirty" dependency
from pathlib import Path
from ..domain.models import TranscriptionJob, TranscriptionResult
from ..domain.interfaces import ITranscriber
from ..exceptions.errors import TranscriptionError, WhisperModelError
from ..config import settings

# Set up logging for this module
log = logging.getLogger(__name__)
log.setLevel(settings.LOG_LEVEL)
if not log.handlers:
    log.addHandler(logging.StreamHandler())
    log.handlers[0].setLevel(settings.LOG_LEVEL)

class WhisperTranscriber(ITranscriber):
    """
    A concrete implementation of ITranscriber that uses the
    local openai-whisper library.
    """
    
    def __init__(self, model_name: str):
        """
        Initializes the extractor and loads the Whisper model into VRAM.
        
        Args:
            model_name: The name of the Whisper model to load (e.g., "small").
        """
        self.model_name = model_name
        self.model = self._load_model()

    def _load_model(self) -> whisper.Whisper:
        """
        Loads the specified Whisper model.
        This is where the VRAM is allocated.
        This will download the model on the first run.
        """
        try:
            log.info(f"Loading Whisper model: '{self.model_name}'...")
            
            # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
            # ARCHITECTURAL FIX:
            # We are explicitly setting device="cpu" because the test
            # environment (GTX 1050 Ti) has an old CUDA capability (6.1)
            # that is not supported by the modern PyTorch build (7.0+).
            # This forces the model to run on the CPU, which will be slow
            # but will prevent the 'no kernel image' crash.
            #
            # When we upgrade to the 3060, we can remove 'device="cpu"'
            # to get full GPU acceleration.
            # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
            model = whisper.load_model(self.model_name, device="cpu")
            
            log.info(f"Whisper model '{self.model_name}' loaded successfully on device 'cpu'.")
            return model
            
        except Exception as e:
            # This could fail due to invalid model name,
            # or CUDA OOM (Out of Memory) error.
            log.error(f"Failed to load Whisper model '{self.model_name}': {e}", exc_info=True)
            raise WhisperModelError(f"Failed to load model '{self.model_name}'. Is it installed? Is there enough VRAM? Error: {e}") from e

    def transcribe(self, job: TranscriptionJob) -> TranscriptionResult:
        """
        Executes the transcription using the loaded Whisper model.
        
        Args:
            job: The TranscriptionJob data model.
        
        Raises:
            TranscriptionError: If the whisper.transcribe() call fails.
        
        Returns:
            A TranscriptionResult model.
        """
        log.info(f"Starting transcription for: {job.audio_file_path}")
        
        try:
            # Check if GPU is available to set fp16
            # This will now correctly be 'False' since we loaded on 'cpu'
            use_fp16 = self.model.device.type == 'cuda'
            if not use_fp16:
                log.warning("Running transcription on CPU. This may be slow.")

            # This is the core work: calling the model's transcribe method
            result_dict = self.model.transcribe(
                str(job.audio_file_path.resolve()),
                fp16=use_fp16 
            )
            
            log.info(f"Transcription successful for: {job.audio_file_path}")
            
            # 4. Map the "dirty" dict result to our "pure" domain model
            return TranscriptionResult(
                text=result_dict.get("text", ""),
                language=result_dict.get("language", "unknown"),
                segments=result_dict.get("segments", [])
            )

        except Exception as e:
            # Catch any generic error during the transcription process
            log.error(f"Transcription failed for file {job.audio_file_path}: {e}", exc_info=True)
            raise TranscriptionError(f"Transcription failed: {e}") from e