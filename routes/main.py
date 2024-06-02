import logging
import uuid
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    send_file,
    session,
    current_app,
)
from werkzeug.utils import secure_filename
from pathlib import Path
from file_processing import process_files
from utils import allowed_file, clear_directory, upload_to_gcs, download_from_gcs

main_bp = Blueprint("main", __name__)


@main_bp.route("/set_dark_mode", methods=["POST"])
def set_dark_mode():
    dark_mode = request.form.get("dark_mode")
    session["dark_mode"] = dark_mode
    return jsonify({"dark_mode": dark_mode})


@main_bp.route("/get_dark_mode", methods=["GET"])
def get_dark_mode():
    dark_mode = session.get("dark_mode", "false")
    return jsonify({"dark_mode": dark_mode})


@main_bp.route("/check_status", methods=["GET"])
def check_status():
    transcription_in_progress = session.get("transcription_in_progress", False)
    return jsonify({"transcription_in_progress": transcription_in_progress})


@main_bp.route("/", methods=["GET", "POST"])
def upload_files():
    try:
        logging.info("Home Page endpoint hit")
        if request.method == "POST":
            if session.get("transcription_in_progress"):
                return (
                    jsonify({"error": "A transcription is already in progress."}),
                    400,
                )

            if "files" not in request.files:
                logging.error("No files part in request")
                return jsonify({"message": "No files part"}), 400

            files = request.files.getlist("files")

            if "session_id" not in session:
                session["session_id"] = str(uuid.uuid4())
            session_id = session["session_id"]
            logging.info(f"Session ID: {session_id}")

            session_uploads_dir = Path(current_app.config["UPLOADS_DIR"]) / session_id
            session_transcriptions_dir = (
                Path(current_app.config["TRANSCRIPTIONS_DIR"]) / session_id
            )
            session_non_wave_files_dir = (
                Path(current_app.config["NON_WAVE_FILES_DIR"]) / session_id
            )

            # Clear previous session directories
            if session_uploads_dir.exists():
                clear_directory(session_uploads_dir)
            if session_transcriptions_dir.exists():
                clear_directory(session_transcriptions_dir)
            if session_non_wave_files_dir.exists():
                clear_directory(session_non_wave_files_dir)

            session_uploads_dir.mkdir(parents=True, exist_ok=True)
            session_transcriptions_dir.mkdir(parents=True, exist_ok=True)
            session_non_wave_files_dir.mkdir(parents=True, exist_ok=True)

            for file in files:
                if file.filename == "":
                    logging.error("No selected file")
                    return jsonify({"message": "No selected file"}), 400
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    local_file_path = session_uploads_dir / filename
                    file.save(local_file_path)
                    logging.info(
                        f"Uploaded file: {filename}, saved to: {local_file_path}"
                    )

                    # Upload to GCS
                    upload_to_gcs(
                        current_app.config["GCS_BUCKET_NAME"],
                        local_file_path,
                        f"{session_id}/{filename}",
                    )

            session["transcription_in_progress"] = True
            session.modified = True

            try:
                process_files(
                    session_uploads_dir,
                    session_transcriptions_dir,
                    session_non_wave_files_dir,
                    session_id,
                )
            except Exception as e:
                logging.error(f"Error during file processing: {e}", exc_info=True)
                session.pop("transcription_in_progress", None)
                session.modified = True
                return jsonify({"message": "Error during file processing"}), 500

            session.pop("transcription_in_progress", None)
            session.modified = True

            return (
                jsonify(
                    {
                        "message": "Files uploaded and processed successfully",
                        "session_id": session_id,
                    }
                ),
                200,
            )

        return render_template("upload_audio.html")
    except Exception as e:
        logging.error(f"Exception occurred in upload_files: {e}", exc_info=True)
        session.pop("transcription_in_progress", None)
        session.modified = True
        return jsonify({"message": "Internal server error"}), 500


@main_bp.route("/download", methods=["GET"])
def download_files():
    try:
        logging.info("Download files endpoint hit")
        session_id = request.args.get("session_id")
        zip_filename = f"processed_files_{session_id}.zip"
        local_zip_path = Path(zip_filename)

        if not local_zip_path.exists():
            logging.info(f"Downloading {zip_filename} from GCS")
            download_from_gcs(
                current_app.config["GCS_BUCKET_NAME"], zip_filename, local_zip_path
            )

        return send_file(local_zip_path, as_attachment=True, download_name=zip_filename)
    except Exception as e:
        logging.error(f"Exception occurred in download_files: {e}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500


@main_bp.route("/cleanup", methods=["POST"])
def cleanup():
    try:
        logging.info("Cleanup endpoint hit")
        if "session_id" in session:
            session_id = session["session_id"]
            logging.info(f"Session ID for cleanup: {session_id}")
            clear_directory(Path(current_app.config["UPLOADS_DIR"]) / session_id)
            clear_directory(Path(current_app.config["TRANSCRIPTIONS_DIR"]) / session_id)
            clear_directory(Path(current_app.config["NON_WAVE_FILES_DIR"]) / session_id)
        return jsonify({"message": "Cleanup successful"}), 200
    except Exception as e:
        logging.error(f"Exception occurred in cleanup: {e}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500
