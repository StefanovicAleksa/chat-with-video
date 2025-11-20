# File: main/features/transcription/service/api.py
"""
This is the Service Layer - The only Public API for this feature.
Other parts of the app (like a GUI or main script) should ONLY import
this function.

Its responsibilities:
1.  Provide a simple, high-level function for the rest of the app.
2.  Perform Dependency Injection: Instantiate the concrete implementation
    (WhisperTranscriber) and inject it into the use case 
    (CreateTranscriptionUseCase).
3.  Handle feature-specific exceptions.
"""

import logging
from pathlib import Path

# --- Concrete Implementation ("Adapter") ---
from ..data.whisper_transcriber import WhisperTranscriber

# --- Pure Domain Logic ("Port" & Models) ---
from ..domain.use_case import CreateTranscriptionUseCase
from ..domain.models import TranscriptionResult

# --- Configuration & Exceptions ---
from ..config import settings
from ..exceptions.errors import TranscriptionError, WhisperModelError

# Set up logging for the service API
log = logging.getLogger(__name__)
log.setLevel(settings.LOG_LEVEL)
if not log.handlers:
    log.addHandler(logging.StreamHandler())
    log.handlers[0].setLevel(settings.LOG_LEVEL)

# --- Public API Function ---

def transcribe_audio(
    audio_file_path: Path | str
) -> TranscriptionResult | None:
    """
    Transcribes an audio file using the local Whisper model.
    
    This function is the main entry point for the transcription feature.
    It performs the Dependency Injection required by the architecture.
    
    Args:
        audio_file_path: The path to the input audio file.
    
    Returns:
        A TranscriptionResult object, or None if transcription failed.
    
    Raises:
        WhisperModelError: If the model (e.g., "small") fails to load.
                           This is a critical setup error.
    """
    log.info(f"Received request to transcribe audio: {audio_file_path}")
    
    try:
        # --- Dependency Injection ---
        
        # 1. Instantiate the concrete implementation (the "Adapter")
        # This is where the model is loaded into VRAM.
        # We use the model name from our new config file.
        transcriber = WhisperTranscriber(
            model_name=settings.DEFAULT_WHISPER_MODEL
        ) 
        
        # 2. Instantiate the pure use case
        # 3. Inject the adapter into the use case
        use_case = CreateTranscriptionUseCase(transcriber=transcriber)
        
        # --- Input Processing ---
        audio_path_obj = Path(audio_file_path)
        log.debug(f"Audio input resolved to: {audio_path_obj.resolve()}")

        # --- Execute ---
        # Call the pure use case, which in turn calls the injected transcriber
        result = use_case.execute(
            audio_path=audio_path_obj
        )
        
        log.info(f"Successfully transcribed file: {audio_file_path}")
        return result

    except WhisperModelError as e:
        # This is a critical setup error (e.g., OOM, model not found).
        # We should let it propagate so the user knows.
        log.error(f"CRITICAL: {e}", exc_info=True)
        raise e 
        
    except TranscriptionError as e:
        # Catch any other feature-specific errors
        log.error(f"Transcription failed: {e}", exc_info=True)
        return None
        
    except Exception as e:
        # Catch any unexpected errors
        log.error(f"An unexpected error occurred: {e}", exc_info=True)
        return None