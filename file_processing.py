import os
import logging
from pathlib import Path
import zipfile
from flask import current_app
from utils import upload_to_gcs, clear_directory
from utils_memory import log_memory_usage
import whisper
import shutil


def process_files(upload_dir, transcriptions_dir, non_wave_files_dir, session_id):
    logging.info(f"Starting file processing for session ID: {session_id}")

    upload_dir_path = Path(upload_dir)
    transcriptions_dir_path = Path(transcriptions_dir)
    non_wave_files_dir_path = Path(non_wave_files_dir)

    # Clear previous session directories
    clear_directory(transcriptions_dir_path)
    clear_directory(non_wave_files_dir_path)

    # List all audio files in the upload directory
    audio_filenames = [
        f
        for f in os.listdir(upload_dir_path)
        if f.endswith((".wav", ".mp3", ".m4a", ".mp4"))
    ]
    logging.info(
        f"Found {len(audio_filenames)} audio files to process for session ID: {session_id}"
    )

    # Initialize whisper model
    model = whisper.load_model("base")
    logging.info("Whisper model loaded successfully")

    transcription_paths = []

    for filename in audio_filenames:
        audio_filepath = upload_dir_path / filename
        audio_filename_stem = Path(filename).stem

        # Run transcription
        transcription = model.transcribe(str(audio_filepath))

        # Create directory for this audio file's transcription
        transcription_dir = transcriptions_dir_path / audio_filename_stem
        transcription_dir.mkdir(parents=True, exist_ok=True)

        # Save transcription files
        for extension, content in zip(
            ["txt", "json", "srt", "vtt"], transcription.values()
        ):
            transcription_filepath = (
                transcription_dir
                / f"{audio_filename_stem}_transcription_with_speakers.{extension}"
            )
            with open(transcription_filepath, "w", encoding="utf-8") as f:
                if isinstance(content, list):
                    for item in content:
                        f.write(str(item))
                else:
                    f.write(str(content))
            logging.info(f"Saved transcription file: {transcription_filepath}")

    logging.info(
        f"Processing complete for session ID: {session_id}. Preparing files for download."
    )
    prepare_files_for_download(transcriptions_dir_path, session_id)

    return transcription_paths


def prepare_files_for_download(transcriptions_dir, session_id):
    try:
        logging.info(f"Preparing files for download for session ID: {session_id}")
        zip_path = Path(f"processed_files_{session_id}.zip")
        if zip_path.exists():
            zip_path.unlink()

        # Log directory contents before zipping
        for root, dirs, files in os.walk(transcriptions_dir):
            for file in files:
                logging.info(f"File in transcriptions directory: {Path(root) / file}")

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
            f"Exception occurred in prepare_files_for_download for session ID: {session_id}: {e}",
            exc_info=True,
        )
