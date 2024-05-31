import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
import zipfile

load_dotenv()

uploads_dir = Path("uploads")
transcriptions_dir = Path("transcriptions")
non_wave_files_dir = Path("non_wave_files")


def process_files():
    try:
        logging.info("Starting file processing")
        auth_token = os.getenv("PYANNOTE_AUTH_TOKEN")
        if not auth_token:
            logging.error("PYANNOTE_AUTH_TOKEN environment variable is not set.")
            return

        service = TranscriptionService(auth_token)
        audio_files = list(uploads_dir.iterdir())

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
        prepare_files_for_download()
    except Exception as e:
        logging.error(f"Exception occurred in process_files: {e}", exc_info=True)


def prepare_files_for_download():
    try:
        logging.info("Preparing files for download")
        zip_path = Path("processed_files.zip")
        if zip_path.exists():
            zip_path.unlink()

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, dirs, files in os.walk(transcriptions_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(transcriptions_dir)
                    zipf.write(file_path, arcname)

        logging.info("Processed files zipped and ready for download.")

        # Cleanup the transcriptions directory
        for root, dirs, files in os.walk(transcriptions_dir, topdown=False):
            for name in files:
                file_path = Path(root) / name
                try:
                    file_path.unlink()
                except PermissionError as e:
                    logging.error(f"PermissionError: {e}")
            for name in dirs:
                dir_path = Path(root) / name
                try:
                    dir_path.rmdir()
                except PermissionError as e:
                    logging.error(f"PermissionError: {e}")

        # Cleanup the non_wave_files directory
        for file in non_wave_files_dir.iterdir():
            try:
                file.unlink()
                logging.info(f"Deleted non-wave file: {file}")
            except PermissionError as e:
                logging.error(f"PermissionError: {e}")
    except Exception as e:
        logging.error(
            f"Exception occurred in prepare_files_for_download: {e}", exc_info=True
        )
