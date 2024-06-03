from celery import shared_task
from file_processing import process_files
import logging


@shared_task(bind=True, queue="transcription-queue")
def transcribe_audio_files(
    self, upload_dir, transcriptions_dir, non_wave_files_dir, session_id
):
    try:
        logging.info(f"Starting transcription task for session ID: {session_id}")
        transcription_paths = process_files(
            upload_dir, transcriptions_dir, non_wave_files_dir, session_id
        )
        for path in transcription_paths:
            logging.info(f"Transcription saved to: {path}")
        logging.info(f"Transcription task completed for session ID: {session_id}")
        return {"status": "completed"}
    except Exception as e:
        logging.error(
            f"Exception in transcription task for session ID: {session_id}: {e}"
        )
        self.retry(exc=e, countdown=60, max_retries=3)
