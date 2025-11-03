import subprocess
import logging
import shlex
import shutil
from pathlib import Path
from ..domain.models import AudioExtractionJob
from ..domain.interfaces import IAudioExtractor
from ..exceptions.errors import FFmpegExecutionError, FFmpegBinaryNotFoundError
from ..config import settings

# Set up logging for this module
log = logging.getLogger(__name__)
log.setLevel(settings.LOG_LEVEL)
# Add a basic console handler if one isn't configured
if not log.handlers:
    log.addHandler(logging.StreamHandler())
    log.handlers[0].setLevel(settings.LOG_LEVEL)

class FFmpegAudioExtractor(IAudioExtractor):
    """
    A concrete implementation of the IAudioExtractor interface that uses
    the ffmpeg command-line tool via subprocess.
    
    This is the "dirty" infrastructure layer.
    """
    
    def __init__(self, ffmpeg_path: str | None = None):
        """
        Initializes the extractor.
        
        Args:
            ffmpeg_path: (Optional) The direct path to the ffmpeg binary.
                         If None, it will be searched for in the system's PATH.
        """
        self.ffmpeg_binary = ffmpeg_path or self._find_ffmpeg()
        if not self.ffmpeg_binary:
            # This check happens at instantiation time.
            raise FFmpegBinaryNotFoundError("ffmpeg binary not found in system's PATH. Please install ffmpeg.")
        log.info(f"Using ffmpeg binary at: {self.ffmpeg_binary}")

    def _find_ffmpeg(self) -> str | None:
        """Uses shutil.which to find the ffmpeg binary in the PATH."""
        return shutil.which("ffmpeg")

    def extract(self, job: AudioExtractionJob) -> None:
        """
        Executes the audio extraction using a subprocess call to ffmpeg.
        
        Args:
            job: The AudioExtractionJob data model.
            
        Raises:
            FFmpegExecutionError: If the subprocess call fails.
        """
        
        # Ensure output directory exists
        job.output_audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build the command.
        # Example:
        # ffmpeg -i "path/to/video.mp4" -vn -q:a 0 "path/to/audio.mp3" -y
        command = [
            self.ffmpeg_binary,
            "-i", str(job.video_file_path.resolve()),  # Input file
            "-vn",                                     # No video
            *job.audio_quality_flags,                  # Audio quality (e.g., ["-q:a", "0"])
            str(job.output_audio_path.resolve()),      # Output file
            "-y"                                       # Overwrite output without asking
        ]
        
        log.info(f"Executing FFmpeg command: {' '.join(shlex.quote(str(c)) for c in command)}")
        
        try:
            # We run the command.
            # We capture output to provide more context on failure.
            # We set a reasonable timeout (e.g., 10 minutes)
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=600
            )
            
            log.info(f"FFmpeg STDOUT: {result.stdout}")
            log.warning(f"FFmpeg STDERR: {result.stderr}")
            log.info(f"Successfully extracted audio to {job.output_audio_path}")

        except subprocess.CalledProcessError as e:
            # This catches non-zero exit codes from ffmpeg
            error_message = (
                f"FFmpeg failed with exit code {e.returncode}.\n"
                f"STDERR: {e.stderr}\n"
                f"STDOUT: {e.stdout}"
            )
            log.error(error_message)
            raise FFmpegExecutionError(error_message) from e
            
        except FileNotFoundError as e:
            # This should be caught by __init__, but as a safeguard
            error_message = f"FFmpeg binary not found at {self.ffmpeg_binary}."
            log.error(error_message)
            raise FFmpegBinaryNotFoundError(error_message) from e

        except subprocess.TimeoutExpired as e:
            error_message = f"FFmpeg command timed out after {e.timeout} seconds."
            log.error(error_message)
            raise FFmpegExecutionError(error_message) from e

