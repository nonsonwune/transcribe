# utils.py
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"wav", "mp3", "mp4", "m4a"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
