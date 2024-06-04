import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_TYPE = "filesystem"
    UPLOADS_DIR = "uploads"
    TRANSCRIPTIONS_DIR = "transcriptions"
    NON_WAVE_FILES_DIR = "non_wave_files"
    PYANNOTE_AUTH_TOKEN = os.getenv("PYANNOTE_AUTH_TOKEN")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )
