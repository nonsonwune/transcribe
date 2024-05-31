import logging
from flask import request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
from app import app, uploads_dir
from utils import allowed_file
from file_processing import process_files, prepare_files_for_download


@app.route("/clear_uploads", methods=["GET"])
def clear_uploads():
    for file in uploads_dir.iterdir():
        file.unlink()
    logging.info("Uploads directory cleared")
    return jsonify({"message": "Uploads directory cleared"}), 200


@app.route("/", methods=["GET", "POST"])
def upload_files():
    try:
        logging.info("Upload files endpoint hit")
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
            return (
                jsonify({"message": "Files uploaded and processed successfully"}),
                200,
            )
        return render_template("upload_audio.html")
    except Exception as e:
        logging.error(f"Exception occurred in upload_files: {e}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/download", methods=["GET"])
def download_files():
    try:
        logging.info("Download files endpoint hit")
        zip_path = Path("processed_files.zip")
        if not zip_path.exists():
            logging.error("No processed files available for download.")
            return (
                jsonify({"message": "No processed files available for download."}),
                400,
            )

        logging.info("Processed files available for download.")
        return send_file(
            zip_path, as_attachment=True, download_name="processed_files.zip"
        )
    except Exception as e:
        logging.error(f"Exception occurred in download_files: {e}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500
