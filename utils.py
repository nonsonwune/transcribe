import logging
from pathlib import Path
import os


def setup_directories(app):
    Path(app.config["UPLOADS_DIR"]).mkdir(exist_ok=True)
    Path(app.config["TRANSCRIPTIONS_DIR"]).mkdir(exist_ok=True)
    Path(app.config["NON_WAVE_FILES_DIR"]).mkdir(exist_ok=True)


def clear_directory(directory):
    for file in Path(directory).iterdir():
        file.unlink()
    Path(directory).rmdir()
    logging.info(f"Directory {directory} cleared")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"wav", "mp3", "mp4", "m4a"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_empty_directories(directory):
    for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
        if not dirnames and not filenames:
            try:
                os.rmdir(dirpath)
                logging.info(f"Removed empty directory: {dirpath}")
            except OSError as e:
                logging.error(f"Error removing directory {dirpath}: {e}")
