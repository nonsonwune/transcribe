import logging
from pathlib import Path
import shutil


def setup_directories(app):
    Path(app.config["UPLOADS_DIR"]).mkdir(exist_ok=True)
    Path(app.config["TRANSCRIPTIONS_DIR"]).mkdir(exist_ok=True)
    Path(app.config["NON_WAVE_FILES_DIR"]).mkdir(exist_ok=True)


def clear_directory(directory):
    if Path(directory).exists():
        shutil.rmtree(directory)
        logging.info(f"Directory {directory} cleared")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"wav", "mp3", "mp4", "m4a"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
