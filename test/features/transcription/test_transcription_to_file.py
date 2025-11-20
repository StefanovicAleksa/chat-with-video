# canvas: test_transcription_to_file_v1
#
# File: test/features/transcription/test_transcription_to_file.py

import pytest
from pathlib import Path
import logging

# --- Imports ---
from main.features.transcription.service.api import transcribe_audio
from main.features.transcription.domain.models import TranscriptionResult

# --- Configuration ---
log = logging.getLogger(__name__)

# We use the same audio file from the previous test
ROOT_DIR = Path(__file__).parent.parent.parent.parent
TEST_AUDIO_FILE = ROOT_DIR / "test_video.mp3"
OUTPUT_TEXT_FILE = ROOT_DIR / "test_transcript.txt"

def check_audio_file():
    if not TEST_AUDIO_FILE.exists():
        pytest.skip(f"Test audio file not found at: {TEST_AUDIO_FILE}")

def test_transcribe_and_save_text():
    """
    Test Case: Transcribe audio and save the full text to a file.
    This allows for manual inspection of the model's output.
    """
    log.info("--- Test: Transcribe and Save to File ---")
    check_audio_file()
    
    # Ensure we start fresh
    if OUTPUT_TEXT_FILE.exists():
        OUTPUT_TEXT_FILE.unlink()

    log.info(f"Input Audio: {TEST_AUDIO_FILE}")
    log.info(f"Output Text: {OUTPUT_TEXT_FILE}")

    try:
        # 1. Run Transcription
        # (This uses the settings from your .env file)
        result = transcribe_audio(TEST_AUDIO_FILE)
        
        assert result is not None
        assert isinstance(result, TranscriptionResult)
        assert len(result.text) > 0
        
        # 2. Write to File
        # We write the text to a simple .txt file
        with open(OUTPUT_TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(f"--- Transcript for {TEST_AUDIO_FILE.name} ---\n")
            f.write(f"Detected Language: {result.language}\n")
            f.write("-" * 40 + "\n\n")
            f.write(result.text.strip())
            
        log.info(f"Successfully saved transcript to: {OUTPUT_TEXT_FILE}")
        
        # 3. Verify File Creation
        assert OUTPUT_TEXT_FILE.exists()
        assert OUTPUT_TEXT_FILE.stat().st_size > 0
        
        # Print a preview to the console
        print(f"\n[Preview] {result.text[:200]}...\n")

    except Exception as e:
        pytest.fail(f"Test failed: {e}")