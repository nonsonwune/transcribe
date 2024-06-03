import os
import logging
from pathlib import Path
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
import zipfile
from flask import current_app
from utils import upload_to_gcs, clear_directory
from utils_memory import log_memory_usage  # Import log_memory_usage from utils_memory


def process_files(upload_dir, transcriptions_dir, non_wave_files_dir, session_id):
    try:
        logging.info("Starting file processing")
        auth_token = os.getenv("PYANNOTE_AUTH_TOKEN")
        if not auth_token:
            logging.error("PYANNOTE_AUTH_TOKEN environment variable is not set.")
            return

        audio_files = list(Path(upload_dir).iterdir())
        if not audio_files:
            logging.error("No audio files found in uploads directory.")
            return

        logging.info(f"Found {len(audio_files)} audio files to process.")

        log_memory_usage()  # Log memory usage before processing

        with Pool(processes=4) as pool:
            pool.map(
                process_audio_file_wrapper,
                [(auth_token, session_id, audio_file) for audio_file in audio_files],
            )

        logging.info("Processing complete. Preparing files for download.")
        prepare_files_for_download(transcriptions_dir, session_id)

        # Clear the uploads directory after processing
        clear_directory(upload_dir)

        log_memory_usage()  # Log memory usage after processing

    except Exception as e:
        logging.error(f"Exception occurred in process_files: {e}", exc_info=True)
        log_memory_usage()  # Log memory usage in case of error


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
