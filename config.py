import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_TYPE = "client"
    UPLOADS_DIR = "uploads"
    TRANSCRIPTIONS_DIR = "transcriptions"
    NON_WAVE_FILES_DIR = "non_wave_files"
    PYANNOTE_AUTH_TOKEN = os.getenv("PYANNOTE_AUTH_TOKEN")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
