import logging

# Log level for the feature
LOG_LEVEL = logging.INFO

# Default Whisper model to use.
# "small" is a good balance for your 1050 Ti's 4GB VRAM.
# Other options: "tiny", "base", "medium", "large"
DEFAULT_WHISPER_MODEL = "medium"