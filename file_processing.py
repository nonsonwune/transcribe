import os
import logging
from pathlib import Path
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
import zipfile


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

        # Ensure the zip file creation
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, dirs, files in os.walk(transcriptions_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(
                        transcriptions_dir
                    )  # Correct relative path
                    logging.info(f"Adding file {file_path} as {arcname} to zip")
                    zipf.write(file_path, arcname)

        logging.info(f"Processed files zipped and ready for download at {zip_path}")
        # Verify zip contents
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipped_files = zipf.namelist()
            logging.info(f"Files in the zip: {zipped_files}")
            if not zipped_files:
                logging.error("No files were added to the zip.")
            else:
                logging.info("Zip file creation successful with files.")

    except Exception as e:
        import os


import logging
from pathlib import Path
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
import zipfile


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
        prepare_files_for_download(transcriptions_dir, session_id)
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
        # Verify zip contents
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipped_files = zipf.namelist()
            logging.info(f"Files in the zip: {zipped_files}")
            if not zipped_files:
                logging.error("No files were added to the zip.")
            else:
                logging.info("Zip file creation successful with files.")

    except Exception as e:
        logging.error(
            f"Exception occurred in prepare_files_for_download: {e}", exc_info=True
        )
