"""
Pytest script for the audio_extraction feature.

To run this test:
1.  Install pytest: pip install pytest
2.  Install the project in editable mode from the root directory:
    pip install -e .
3.  Place 'test_video.mp4' in the project root.
4.  Run 'pytest' from the terminal in the project root.
"""

import logging
from pathlib import Path

# With the project installed via 'pip install -e .',
# we can now import our feature's API directly, no sys.path hacks.
from features.audio_extraction.service.api import extract_audio_from_video
from features.audio_extraction.exceptions.errors import FFmpegBinaryNotFoundError

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s"
)
log = logging.getLogger(__name__)

# --- Test Configuration ---
ROOT_DIR = Path(__file__).parent.parent.parent.parent # Get project root
TEST_VIDEO_FILE = ROOT_DIR / "test_video.mp4" 
# --------------------------

def check_video_file():
    """Helper to check for the video file before running tests."""
    if not TEST_VIDEO_FILE.exists():
        msg = f"Test video file not found at: {TEST_VIDEO_FILE}"
        log.error(msg)
        raise FileNotFoundError(msg)

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
        # ----------------------------

        # --- Check Results ---
        assert result_path is not None
        assert result_path == expected_output
        assert result_path.exists()
        log.info(f"✅ SUCCESS: File created at: {result_path}")
        
    finally:
        # --- Clean up ---
        if expected_output.exists():
            expected_output.unlink()
            log.info(f"Cleaned up {expected_output}")

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
        # ----------------------------

        # --- Check Results ---
        assert result_path is not None
        assert result_path == specified_output
        assert result_path.exists()
        log.info(f"✅ SUCCESS: File created at: {result_path}")

    finally:
        # --- Clean up ---
        if specified_output.exists():
            specified_output.unlink()
            log.info(f"Cleaned up {specified_output}")

