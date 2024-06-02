import logging
from pathlib import Path
import shutil
from google.cloud import storage


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


def get_gcs_client():
    return storage.Client()


def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the GCS bucket."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    logging.info(f"File {source_file_name} uploaded to {destination_blob_name}.")


def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """Downloads a file from the GCS bucket."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)
    logging.info(f"File {source_blob_name} downloaded to {destination_file_name}.")
