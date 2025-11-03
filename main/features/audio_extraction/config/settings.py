import logging

# Log level for the feature
LOG_LEVEL = logging.INFO

# Default audio format to extract
DEFAULT_OUTPUT_FORMAT = "mp3"

# FFmpeg settings
# -q:a 0 sets a variable bitrate (VBR) that produces high-quality audio
# You could also use a constant bitrate (CBR) like "-b:a 192k"
FFMPEG_AUDIO_QUALITY_FLAGS = ["-q:a", "0"]
