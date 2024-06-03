import logging
import uuid
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    session,
    current_app,
    send_file,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from pathlib import Path
from utils import allowed_file, clear_directory, upload_to_gcs
from tasks import transcribe_audio_files
import redis
import zipfile
import os
import tempfile

main_bp = Blueprint("main", __name__)


@main_bp.route("/test_redis", methods=["GET"])
def test_redis():
    try:
        r = redis.Redis(host="localhost", port=6379, db=0)
        r.set("foo", "bar")
        value = r.get("foo")
        return jsonify({"message": f"Redis test successful, value: {value}"})
    except Exception as e:
        logging.error(f"Redis test failed: {e}")
        return jsonify({"message": "Redis test failed"}), 500


@main_bp.route("/check_transcription_status", methods=["GET"])
def check_transcription_status():
    session_id = request.args.get("session_id")
    task_id = session.get("task_id")
    if not task_id:
        return jsonify({"status": "not_started"})

    task_result = transcribe_audio_files.AsyncResult(task_id)
    logging.info(f"Task state for session ID {session_id}: {task_result.state}")

    if task_result.state == "PENDING":
        return jsonify({"status": "in_progress"})
    elif task_result.state == "SUCCESS":
        session["transcription_in_progress"] = False
        session.modified = True
        return jsonify({"status": "completed"})
    elif task_result.state == "FAILURE":
        session["transcription_in_progress"] = False
        session.modified = True
        return jsonify({"status": "failed"})
    else:
        return jsonify({"status": "unknown"})


@main_bp.route("/", methods=["GET", "POST"])
def upload_files():
    try:
        logging.info("Home Page endpoint hit")
        if request.method == "POST":
            if session.get("transcription_in_progress"):
                logging.warning("Transcription already in progress")
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
            clear_directory(session_uploads_dir)
            clear_directory(session_transcriptions_dir)
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

                    # Check if file is saved correctly
                    if not local_file_path.exists():
                        logging.error(
                            f"File {local_file_path} does not exist after saving."
                        )

                    # Upload to GCS
                    try:
                        upload_to_gcs(
                            current_app.config["GCS_BUCKET_NAME"],
                            local_file_path,
                            f"{session_id}/{filename}",
                        )
                        logging.info(
                            f"File {filename} uploaded to GCS as {session_id}/{filename}"
                        )
                    except Exception as e:
                        logging.error(f"Error uploading file to GCS: {e}")

            session["transcription_in_progress"] = True
            session.modified = True

            # Call Celery task
            result = transcribe_audio_files.apply_async(
                args=[
                    str(session_uploads_dir),
                    str(session_transcriptions_dir),
                    str(session_non_wave_files_dir),
                    session_id,
                ],
                queue="transcription-queue",
            )

            session["task_id"] = result.id

            return (
                jsonify(
                    {
                        "message": "Files uploaded successfully and processing started",
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
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    session_transcriptions_dir = (
        Path(current_app.config["TRANSCRIPTIONS_DIR"]) / session_id
    )
    if not session_transcriptions_dir.exists():
        return jsonify({"error": "No files found for the given session ID"}), 404

    zip_filename = f"processed_files_{session_id}.zip"
    zip_filepath = Path(current_app.config["TRANSCRIPTIONS_DIR"]) / zip_filename

    try:
        with zipfile.ZipFile(zip_filepath, "w") as zf:
            for root, dirs, files in os.walk(session_transcriptions_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(session_transcriptions_dir)
                    logging.info(f"Adding file {file_path} as {arcname} to zip")
                    zf.write(file_path, arcname)

        if not zip_filepath.exists():
            return jsonify({"error": "Failed to create zip file"}), 500

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / zip_filename
            zip_filepath.rename(temp_zip_path)
            try:
                return send_from_directory(
                    temp_dir,
                    zip_filename,
                    as_attachment=True,
                    download_name=zip_filename,
                )
            finally:
                temp_zip_path.unlink()

    except Exception as e:
        logging.error(f"Exception occurred in download_files: {e}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500
