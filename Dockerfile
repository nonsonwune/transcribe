# Use the official Python image from the Docker Hub
FROM python:3.10

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --upgrade pip

# Install the Python dependencies with a mirror
RUN pip install --default-timeout=1000 -r requirements.txt

# Set environment variables
ENV PYANNOTE_AUTH_TOKEN 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

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--timeout", "120", "app:app"]
