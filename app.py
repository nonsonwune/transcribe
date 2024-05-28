import os
import logging
from pathlib import Path
from flask import Flask, request, send_file, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
from utils import allowed_file
from time import sleep
import shutil
import zipfile

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

# Ensure the uploads directory exists
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Ensure the transcriptions directory exists
transcriptions_dir = Path("transcriptions")
transcriptions_dir.mkdir(exist_ok=True)


@app.route("/clear_uploads", methods=["GET"])
def clear_uploads():
    for file in uploads_dir.iterdir():
        file.unlink()
    logging.info("Uploads directory cleared")
    return jsonify({"message": "Uploads directory cleared"}), 200


@app.route("/", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST":
        if "files" not in request.files:
            logging.error("No files part in request")
            return jsonify({"message": "No files part"}), 400
        files = request.files.getlist("files")
        for file in files:
            if file.filename == "":
                logging.error("No selected file")
                return jsonify({"message": "No selected file"}), 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = uploads_dir / filename
                file.save(file_path)
                logging.info(f"Uploaded file: {filename}, saved to: {file_path}")

        # Process files immediately after upload
        process_files()
        return jsonify({"message": "Files uploaded and processed successfully"}), 200
    return render_template("upload_audio.html")


def process_files():
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


def prepare_files_for_download():
    zip_path = Path("processed_files.zip")
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in transcriptions_dir.iterdir():
            try:
                zipf.write(file, arcname=file.name)
            except PermissionError:
                logging.error(f"Could not add {file} to zip due to permission issues.")

    for file in transcriptions_dir.iterdir():
        try:
            file.unlink()
        except PermissionError:
            logging.error(f"Could not delete {file} due to permission issues.")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
