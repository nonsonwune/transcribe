import os
import logging
from pathlib import Path
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
from utils import allowed_file
import zipfile

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

# Ensure the directories exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
transcriptions_dir = Path("transcriptions")
transcriptions_dir.mkdir(exist_ok=True)
non_wave_files_dir = Path("non_wave_files")
non_wave_files_dir.mkdir(exist_ok=True)


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


@app.route("/download", methods=["GET"])
def download_files():
    zip_path = Path("processed_files.zip")
    if not zip_path.exists():
        logging.error("No processed files available for download.")
        return jsonify({"message": "No processed files available for download."}), 400

    logging.info("Processed files available for download.")
    return send_file(zip_path, as_attachment=True, download_name="processed_files.zip")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
