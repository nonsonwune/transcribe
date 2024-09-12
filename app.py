from flask import Flask, session, jsonify, request, render_template, send_file
from flask_session import Session
from config import Config
from routes import main_bp
import logging
from utils import setup_directories, allowed_file
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import zipfile
from transcription_service import TranscriptionService
from multiprocessing import Pool

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup session management
    Session(app)

    # Ensure necessary directories exist
    with app.app_context():
        setup_directories(app)

    # Register blueprint
    app.register_blueprint(main_bp)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.route("/clear_uploads", methods=["GET"])
    def clear_uploads():
        uploads_dir = Path(app.config["UPLOAD_FOLDER"])
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
            uploads_dir = Path(app.config["UPLOAD_FOLDER"])
            for file in files:
                if file.filename == "":
                    logging.error("No selected file")
                    return jsonify({"message": "No selected file"}), 400
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = uploads_dir / filename
                    file.save(file_path)
                    logging.info(f"Uploaded file: {filename}, saved to: {file_path}")
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
        uploads_dir = Path(app.config["UPLOAD_FOLDER"])
        audio_files = list(uploads_dir.iterdir())

        if not audio_files:
            logging.error("No audio files found in uploads directory.")
            return (
                jsonify({"message": "No audio files found in uploads directory."}),
                400,
            )

        logging.info(f"Found {len(audio_files)} audio files to process.")

        with Pool(processes=4) as pool:
            pool.map(
                process_audio_file_wrapper,
                [(service, audio_file) for audio_file in audio_files],
            )

        logging.info("Processing complete. Preparing files for download.")
        prepare_files_for_download(app)
        return jsonify({"message": "Transcription completed."}), 200

    @app.route("/download", methods=["GET"])
    def download_files():
        zip_path = Path("processed_files.zip")
        if not zip_path.exists():
            logging.error("No processed files available for download.")
            return (
                jsonify({"message": "No processed files available for download."}),
                400,
            )

        logging.info("Processed files available for download.")

        response = send_file(
            zip_path, as_attachment=True, download_name="processed_files.zip"
        )

        # Cleanup the uploads directory
        uploads_dir = Path(app.config["UPLOAD_FOLDER"])
        for file in uploads_dir.iterdir():
            file.unlink()

        return response

    return app


def prepare_files_for_download(app):
    zip_path = Path("processed_files.zip")
    if zip_path.exists():
        zip_path.unlink()

    transcriptions_dir = Path(app.config["TRANSCRIPTIONS_FOLDER"])
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


# for gunicorn
app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)
