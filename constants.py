import os

# paths definition and data loading
DATA_DIR = "data_to_analyze"
SPOTIFY_STREAMING_FILE_NAME = "Spotify Extended Streaming History"
SPOTIFY_ACCOUNT_DATA_FILE_NAME = "Spotify Account Data"

AUDIO_VIDEO_PATH = os.path.join(DATA_DIR, SPOTIFY_STREAMING_FILE_NAME)
ACCOUNT_DATA_PATH = os.path.join(DATA_DIR, SPOTIFY_ACCOUNT_DATA_FILE_NAME)
