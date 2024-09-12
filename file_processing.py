import os
import logging
from pathlib import Path
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
import zipfile
from utils import cleanup_empty_directories


def process_files(upload_dir, transcriptions_dir, non_wave_files_dir, session_id):
    try:
        logging.info("Starting file processing")
        auth_token = os.getenv("PYANNOTE_AUTH_TOKEN")
        if not auth_token:
            logging.error("PYANNOTE_AUTH_TOKEN environment variable is not set.")
            return

        service = TranscriptionService(auth_token, session_id)

        audio_files = list(Path(upload_dir).iterdir())
        if not audio_files:
            logging.error("No audio files found in uploads directory.")
            return

        logging.info(f"Found {len(audio_files)} audio files to process.")

        with Pool(processes=4) as pool:
            pool.map(
                process_audio_file_wrapper,
                [(service, audio_file) for audio_file in audio_files],
            )

        logging.info("Processing complete. Preparing files for download.")
        prepare_files_for_download(transcriptions_dir / session_id, session_id)
    except Exception as e:
        logging.error(f"Exception occurred in process_files: {e}", exc_info=True)


def prepare_files_for_download(transcriptions_dir, session_id):
    try:
        logging.info(f"Preparing files for download for session ID: {session_id}")
        zip_path = Path(f"processed_files_{session_id}.zip")
        if zip_path.exists():
            zip_path.unlink()

        cleanup_empty_directories(transcriptions_dir)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, dirs, files in os.walk(transcriptions_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(transcriptions_dir)
                    logging.info(f"Adding file {file_path} as {arcname} to zip")
                    zipf.write(file_path, arcname)

        if zipfile.is_zipfile(zip_path):
            with zipfile.ZipFile(zip_path, "r") as zipf:
                zipped_files = zipf.namelist()
                if zipped_files:
                    logging.info(f"Zip file creation successful. Files: {zipped_files}")
                    return True
                else:
                    logging.error("Zip file created but contains no files.")
                    return False
        else:
            logging.error("Failed to create a valid zip file.")
            return False

    except Exception as e:
        logging.error(
            f"Exception occurred in prepare_files_for_download: {e}", exc_info=True
        )
        return False
