import logging
from flask import request, jsonify, render_template, send_file, session
from werkzeug.utils import secure_filename
from pathlib import Path
from app import app, base_uploads_dir, base_transcriptions_dir, base_non_wave_files_dir
from utils import (
    allowed_file,
    clear_session_uploads,
    clear_session_transcriptions,
    clear_session_non_wave_files,
)
from file_processing import process_files, prepare_files_for_download


@app.route("/set_dark_mode", methods=["POST"])
def set_dark_mode():
    dark_mode = request.form.get("dark_mode")
    session["dark_mode"] = dark_mode
    return jsonify({"dark_mode": dark_mode})


@app.route("/get_dark_mode", methods=["GET"])
def get_dark_mode():
    dark_mode = session.get("dark_mode", "false")
    return jsonify({"dark_mode": dark_mode})


@app.route("/", methods=["GET", "POST"])
def upload_files():
    try:
        logging.info("Upload files endpoint hit")
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
            session_id = session.sid
            session_uploads_dir = base_uploads_dir / session_id
            session_transcriptions_dir = base_transcriptions_dir / session_id
            session_non_wave_files_dir = base_non_wave_files_dir / session_id
            session_uploads_dir.mkdir(exist_ok=True)
            session_transcriptions_dir.mkdir(exist_ok=True)
            session_non_wave_files_dir.mkdir(exist_ok=True)

            for file in files:
                if file.filename == "":
                    logging.error("No selected file")
                    return jsonify({"message": "No selected file"}), 400
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = session_uploads_dir / filename
                    file.save(file_path)
                    logging.info(f"Uploaded file: {filename}, saved to: {file_path}")

            session["transcription_in_progress"] = True
            session.modified = True  # Mark the session as modified to trigger save

            # Process files immediately after upload
            process_files(
                session_uploads_dir,
                session_transcriptions_dir,
                session_non_wave_files_dir,
                session_id,
            )
            session.pop("transcription_in_progress", None)
            session.modified = True
            clear_session_uploads(session_id)
            clear_session_transcriptions(session_id)
            clear_session_non_wave_files(session_id)
            return (
                jsonify({"message": "Files uploaded and processed successfully"}),
                200,
            )
        return render_template("upload_audio.html")
    except Exception as e:
        logging.error(f"Exception occurred in upload_files: {e}", exc_info=True)
        session_id = session.sid
        session.pop("transcription_in_progress", None)
        session.modified = True
        clear_session_uploads(session_id)
        clear_session_transcriptions(session_id)
        clear_session_non_wave_files(session_id)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/download", methods=["GET"])
def download_files():
    try:
        logging.info("Download files endpoint hit")
        session_id = session.sid
        zip_path = Path(f"processed_files_{session_id}.zip")
        if not zip_path.exists():
            logging.error("No processed files available for download.")
            return (
                jsonify({"message": "No processed files available for download."}),
                400,
            )

        logging.info("Processed files available for download.")
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"processed_files_{session_id}.zip",
        )
    except Exception as e:
        logging.error(f"Exception occurred in download_files: {e}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500
