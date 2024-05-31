import os
import logging
from flask import Flask
from dotenv import load_dotenv
from pathlib import Path

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

# Import routes
from routes import *

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
