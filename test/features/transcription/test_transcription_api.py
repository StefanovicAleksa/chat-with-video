# File: test/features/transcription/test_transcription_api.py
import pytest
from pathlib import Path
import logging

# --- Imports from our application code in 'main' ---

# 1. The public API function we are testing
from main.features.transcription.service.api import transcribe_audio

# 2. The data model we expect to get back
from main.features.transcription.domain.models import TranscriptionResult

# 3. The custom exceptions our API might raise
from main.features.transcription.exceptions.errors import (
    TranscriptionError, 
    WhisperModelError
)

# --- Test Configuration ---
log = logging.getLogger(__name__)

# This test requires the audio file 'test_video.mp3',
# which should have been created by 'test_audio_extraction_api.py'
ROOT_DIR = Path(__file__).parent.parent.parent.parent # Get project root
TEST_AUDIO_FILE = ROOT_DIR / "test_video.mp3"
# --------------------------

def check_audio_file():
    """Helper function to skip tests if the audio file is missing."""
    if not TEST_AUDIO_FILE.exists():
        pytest.skip(f"Test audio file not found at: {TEST_AUDIO_FILE}. "
                    "Run the audio_extraction test first to create it.")

# --- Test Case ---

def test_transcribe_audio_success():
    """
    Test Case 1: Transcribe a known audio file and check the result.
    
    This is an integration test. It will:
    1. Load the 'small' Whisper model into VRAM.
    2. Run the transcription on a real audio file.
    3. Check the format of the output.
    """
    log.info("--- Test: Transcribe Audio Success ---")
    check_audio_file()
    
    log.info(f"Testing transcription for: {TEST_AUDIO_FILE}")
    
    try:
        # --- Call the Feature API ---
        # This will load the 'small' model into VRAM
        result = transcribe_audio(
            audio_file_path=TEST_AUDIO_FILE
        )
        
        # --- Assert ---
        assert result is not None, "The transcription result should not be None."
        
        # Check that we got back the correct object type
        assert isinstance(result, TranscriptionResult)
        
        # Check the contents of the result
        assert result.text is not None, "Transcription text should not be None."
        assert isinstance(result.text, str)
        # We assume the test audio has *some* speech
        assert len(result.text) > 0, "Transcription text should not be empty."
        
        assert result.language is not None
        assert len(result.language) > 0 # e.g., "en"
        
        log.info("Test Passed: Transcription successful.")
        log.info(f"Detected language: {result.language}")
        log.info(f"Transcription snippet: {result.text[:100]}...")

    except (WhisperModelError, TranscriptionError) as e:
        log.error(f"Test Failed with a TranscriptionError: {e}", exc_info=True)
        pytest.fail(f"TranscriptionError or WhisperModelError occurred: {e}")
        
    except Exception as e:
        log.error(f"Test Failed with an unexpected error: {e}", exc_info=True)
        pytest.fail(f"Unexpected error occurred: {e}")