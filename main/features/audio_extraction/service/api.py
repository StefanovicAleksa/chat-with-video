"""
This is the Service Layer - The only Public API for this feature.

This is the *only* file that other parts of the application (like the
Streamlit GUI) should import from.

Its responsibilities:
1.  Provide a simple, high-level function for the rest of the app.
2.  Perform Dependency Injection: Instantiate the concrete implementations
    (from the `data` layer) and inject them into the use case (from the
    `domain` layer).
3.  Handle feature-specific exceptions and re-raise them or return a
    safe value.
"""

import logging
from pathlib import Path

# --- Concrete Implementation ---
# We import the *concrete* class from the data layer
from ..data.ffmpeg_extractor import FFmpegAudioExtractor

# --- Pure Domain Logic ---
# We import the *pure* use case from the domain layer
from ..domain.use_case import ExtractAudioUseCase

# --- Configuration & Exceptions ---
from ..config import settings
from ..exceptions.errors import AudioExtractionError, FFmpegBinaryNotFoundError

# Set up logging for the service API
log = logging.getLogger(__name__)
log.setLevel(settings.LOG_LEVEL)
if not log.handlers:
    log.addHandler(logging.StreamHandler())
    log.handlers[0].setLevel(settings.LOG_LEVEL)

# --- Public API Function ---

def extract_audio_from_video(
    video_file_path: Path | str,
    output_audio_path: Path | str | None = None
) -> Path | None:
    """
    Extracts audio from a video file and saves it as an MP3.

    This function is the main entry point for the audio_extraction feature.
    It performs the dependency injection required by the architecture.

    Args:
        video_file_path: The path to the input video file.
        output_audio_path: (Optional) The desired path for the output audio.
                           If None, it defaults to a .mp3 file with the
                           same name in the same directory.

    Returns:
        The Path to the created audio file, or None if extraction failed.
        
    Raises:
        FFmpegBinaryNotFoundError: If the ffmpeg binary is not installed.
        AudioExtractionError: For other extraction-related failures.
    """
    log.info(f"Received request to extract audio from: {video_file_path}")
    
    try:
        # --- Dependency Injection ---
        # 1. Instantiate the concrete implementation (the "Adapter")
        # This might fail if ffmpeg isn't installed.
        extractor = FFmpegAudioExtractor() 
        
        # 2. Instantiate the pure use case (the "Port")
        # 3. Inject the adapter into the port
        use_case = ExtractAudioUseCase(extractor=extractor)
        
        # --- Input Processing ---
        # Ensure paths are Path objects
        video_path_obj = Path(video_file_path)
        
        # Default output path logic
        if output_audio_path:
            output_path_obj = Path(output_audio_path)
        else:
            output_path_obj = video_path_obj.with_suffix(f".{settings.DEFAULT_OUTPUT_FORMAT}")
        
        log.debug(f"Video input resolved to: {video_path_obj.resolve()}")
        log.debug(f"Audio output resolved to: {output_path_obj.resolve()}")

        # --- Execute ---
        # Call the pure use case, which in turn calls the injected extractor
        created_audio_file = use_case.execute(
            video_path=video_path_obj,
            output_path=output_path_obj,
            quality_flags=settings.FFMPEG_AUDIO_QUALITY_FLAGS
        )
        
        log.info(f"Successfully created audio file: {created_audio_file}")
        return created_audio_file

    except FFmpegBinaryNotFoundError as e:
        # This is a critical setup error. We should let it propagate
        # so the user (or GUI) knows the dependency is missing.
        log.error(f"CRITICAL: {e}")
        raise e 
        
    except AudioExtractionError as e:
        # Catch any other feature-specific errors
        log.error(f"Audio extraction failed: {e}", exc_info=True)
        return None
        
    except Exception as e:
        # Catch any unexpected errors
        log.error(f"An unexpected error occurred: {e}", exc_info=True)
        return None

