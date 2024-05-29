# Audio Transcription Service

This project provides an audio transcription service that allows users to upload audio files, perform speaker diarization, and download the transcribed text files in various formats.

## Features

- Upload audio files in various formats.
- Automatic conversion of non-WAV files to WAV format.
- Transcribe audio using Whisper.
- Perform speaker diarization using pyannote.audio.
- Download transcribed files in TXT, JSON, SRT, and VTT formats.
- Dark mode toggle for the user interface.

## Project Structure

```
.
├── README.md
├── __pycache__
├── app.py
├── non_wave_files
├── processed_files.zip
├── requirements.txt
├── static
│   ├── scripts.js
│   └── styles.css
├── templates
│   └── upload_audio.html
├── transcription_service.py
├── transcriptions
├── uploads
└── utils.py
```

## Requirements

To install the required packages, run:

```
pip install -r requirements.txt
```

## Usage

1. **Start the Flask server:**

   ```bash
   python app.py
   ```

2. **Access the web interface:**

   Open a web browser and go to `http://localhost:5000`.

3. **Upload and transcribe audio files:**

   - Select the audio file(s) you want to transcribe.
   - Click the "Transcribe" button.
   - Wait for the transcription process to complete.
   - Download the transcribed files.

## File Details

### app.py

The main Flask application that handles file uploads, processing, and download of transcribed files.

### transcription_service.py

Contains the `TranscriptionService` class, which handles audio file conversion, transcription, speaker diarization, and saving the results in different formats.

### static/scripts.js

JavaScript file for handling frontend functionality, including form submission, dark mode toggle, and AJAX requests.

### templates/upload_audio.html

HTML template for the web interface, providing a form for file upload and buttons for transcription and download.

### utils.py

Utility functions used in the project, such as checking allowed file types.

## Environment Variables

Create a `.env` file in the project root and add your `PYANNOTE_AUTH_TOKEN`:

```
PYANNOTE_AUTH_TOKEN=your_pyannote_token_here
```

## Notes

- Ensure you have a valid `PYANNOTE_AUTH_TOKEN` for the speaker diarization service.
- The project supports multiprocessing for efficient audio file processing.
- Uploaded files are automatically cleared after processing to save space.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

```

## GitHub Repository

The project is hosted on a private GitHub repository. For more information, visit: [GitHub Repository](https://github.com/nonsonwune/transcribe)
```
