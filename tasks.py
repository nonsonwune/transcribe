import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from transcription_service import TranscriptionService, process_audio_file_wrapper
import zipfile
from celery_app import celery
from utils import upload_to_gcs, clear_directory
from flask import current_app, Flask
import os

# Create a dummy app context for standalone script execution
app = Flask(__name__)
app.config.from_object("config.Config")


@celery.task
def process_files_task(upload_dir, transcriptions_dir, non_wave_files_dir, session_id):
    try:
        logging.info("Starting file processing")
        auth_token = os.getenv("PYANNOTE_AUTH_TOKEN")
        if not auth_token:
            logging.error("PYANNOTE_AUTH_TOKEN environment variable is not set.")
            return

        service = TranscriptionService(auth_token, session_id)

        upload_dir = Path(upload_dir)
        transcriptions_dir = Path(transcriptions_dir)
        non_wave_files_dir = Path(non_wave_files_dir)

        audio_files = list(upload_dir.iterdir())
        if not audio_files:
            logging.error("No audio files found in uploads directory.")
            return

        logging.info(f"Found {len(audio_files)} audio files to process.")

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_audio_file_wrapper, (service, audio_file))
                for audio_file in audio_files
            ]
            for future in futures:
                future.result()

        logging.info("Processing complete. Preparing files for download.")
        with app.app_context():
            prepare_files_for_download(transcriptions_dir, session_id)

        clear_directory(upload_dir)

    except Exception as e:
        logging.error(f"Exception occurred in process_files: {e}", exc_info=True)


def prepare_files_for_download(transcriptions_dir, session_id):
    try:
        logging.info(f"Preparing files for download for session ID: {session_id}")
        zip_path = Path(f"processed_files_{session_id}.zip")
        if zip_path.exists():
            zip_path.unlink()

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, dirs, files in os.walk(transcriptions_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(transcriptions_dir)
                    logging.info(f"Adding file {file_path} as {arcname} to zip")
                    zipf.write(file_path, arcname)

        logging.info(f"Processed files zipped and ready for download at {zip_path}")
        upload_to_gcs(current_app.config["GCS_BUCKET_NAME"], zip_path, zip_path.name)
    except Exception as e:
        logging.error(
            f"Exception occurred in prepare_files_for_download: {e}", exc_info=True
        )


@celery.task
def transcription_complete(session_id, **kwargs):
    with app.app_context():
        session = celery.flask_app.extensions["flask-session"].open_session(
            celery.flask_app
        )
        session["transcription_in_progress"] = False
        session.modified = True
        session.save()
