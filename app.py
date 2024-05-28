# app.py
import os
import logging
from pathlib import Path
from flask import (
    Flask,
    request,
    send_from_directory,
    send_file,
    render_template,
    redirect,
    url_for,
    jsonify,
)
import zipfile
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from multiprocessing import Pool
from transcription_service import TranscriptionService, process_audio_file_wrapper
from utils import allowed_file

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
    return jsonify({"message": "Uploads directory cleared"}), 200


@app.route("/", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST":
        if "files" not in request.files:
            return jsonify({"message": "No files part"}), 400
        files = request.files.getlist("files")
        for file in files:
            if file.filename == "":
                return jsonify({"message": "No selected file"}), 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(uploads_dir, filename))
        return jsonify({"message": "Files uploaded successfully"}), 200
    return render_template("upload_audio.html")


@app.route("/process", methods=["GET"])
def process_files():
    auth_token = os.getenv("PYANNOTE_AUTH_TOKEN")
    if not auth_token:
        logging.error("PYANNOTE_AUTH_TOKEN environment variable is not set.")
        return (
            jsonify(
                {"message": "PYANNOTE_AUTH_TOKEN environment variable is not set."}
            ),
            400,
        )

    service = TranscriptionService(auth_token)
    audio_files = list(uploads_dir.iterdir())

    with Pool(processes=4) as pool:
        pool.map(
            process_audio_file_wrapper,
            [(service, audio_file) for audio_file in audio_files],
        )

    return redirect(url_for("download_files"))


@app.route("/check_processing", methods=["GET"])
def check_processing():
    uploaded_files = [f.name for f in uploads_dir.iterdir() if f.is_file()]
    processing_complete = all(
        any(
            Path(transcriptions_dir, f"{Path(file).stem}.{ext}").exists()
            for ext in ["txt", "json", "srt", "vtt"]
        )
        for file in uploaded_files
    ) and not any(uploads_dir.iterdir())

    return jsonify({"processingComplete": processing_complete})


@app.route("/download", methods=["GET"])
def download_files():
    if not any(transcriptions_dir.iterdir()):
        return jsonify({"message": "No processed files available for download."}), 400

    zip_path = Path("processed_files.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, dirs, files in os.walk(transcriptions_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, transcriptions_dir)
                zipf.write(file_path, arcname)
    for file in uploads_dir.iterdir():
        file.unlink()

    return send_file(zip_path, as_attachment=True, download_name="processed_files.zip")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
