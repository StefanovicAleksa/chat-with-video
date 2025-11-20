import pytest
from pathlib import Path
import logging

# We must import from the 'main' package, which is installable
# due to our pyproject.toml and 'pip install -e .'
from main.features.audio_extraction.service.api import extract_audio_from_video
from main.features.audio_extraction.exceptions.errors import AudioExtractionError

# --- Test Configuration ---
log = logging.getLogger(__name__)

# This test requires a real video file named 'test_video.mp4' in the root.
ROOT_DIR = Path(__file__).parent.parent.parent.parent # Get project root
TEST_VIDEO_FILE = ROOT_DIR / "test_video.mp4"
# --------------------------

def check_video_file():
    """Helper function to skip tests if the video file is missing."""
    if not TEST_VIDEO_FILE.exists():
        pytest.skip(f"Test video file not found at: {TEST_VIDEO_FILE}")

# --- Test Cases ---

def test_default_output():
    """
    Test Case 1: Let the function decide the output path.
    (e.g., test_video.mp4 -> test_video.mp3)
    """
    log.info("--- Test 1: Default Output Path ---")
    check_video_file()
    
    expected_output = TEST_VIDEO_FILE.with_suffix(".mp3")
    log.info(f"Expected output audio: {expected_output}")
    
    try:
        # --- Call the Feature API ---
        result_path = extract_audio_from_video(
            video_file_path=TEST_VIDEO_FILE
        )
        
        # --- Assert ---
        assert result_path == expected_output
        assert result_path.exists()
        assert result_path.stat().st_size > 0 # File is not empty
        log.info("Test 1 Passed: Default output file created successfully.")
        
    except AudioExtractionError as e:
        log.error(f"Test 1 Failed with an AudioExtractionError: {e}")
        pytest.fail(f"AudioExtractionError occurred: {e}")
    except Exception as e:
        log.error(f"Test 1 Failed with an unexpected error: {e}")
        pytest.fail(f"Unexpected error occurred: {e}")
        
    # finally:
    #     # --- Clean up (COMMENTED OUT) ---
    #     # This is commented out so the file 'test_video.mp3' remains
    #     # for the transcription test.
    #     if expected_output.exists():
    #         # expected_output.unlink()
    #         log.info("Clean up skipped for transcription test.")


def test_specified_output():
    """
    Test Case 2: We specify a custom output path.
    """
    log.info("--- Test 2: Specified Output Path ---")
    check_video_file()
    
    specified_output = ROOT_DIR / "my_custom_audio_output.mp3"
    log.info(f"Specified output audio: {specified_output}")
    
    # Ensure it doesn't exist before we start
    if specified_output.exists():
        specified_output.unlink()
        log.info("Removed old file before test.")
        
    try:
        # --- Call the Feature API ---
        result_path = extract_audio_from_video(
            video_file_path=TEST_VIDEO_FILE,
            output_audio_path=specified_output
        )
        
        # --- Assert ---
        assert result_path == specified_output
        assert result_path.exists()
        assert result_path.stat().st_size > 0
        log.info("Test 2 Passed: Specified output file created successfully.")

    except AudioExtractionError as e:
        log.error(f"Test 2 Failed with an AudioExtractionError: {e}")
        pytest.fail(f"AudioExtractionError occurred: {e}")
    except Exception as e:
        log.error(f"Test 2 Failed with an unexpected error: {e}")
        pytest.fail(f"Unexpected error occurred: {e}")
        
    # finally:
    #     # --- Clean up (COMMENTED OUT) ---
    #     if specified_output.exists():
    #         # specified_output.unlink()
    #         log.info("Clean up skipped.")

