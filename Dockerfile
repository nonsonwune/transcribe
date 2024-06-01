# Use the official Python image from the Docker Hub
FROM python:3.10-slim-buster

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt early to leverage Docker cache
COPY requirements.txt .

# Copy the current directory contents into the container at /app
COPY . /app

# Install the Python dependencies
RUN pip install -r requirements.txt

# Set environment variables
ENV PYANNOTE_AUTH_TOKEN=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
ENV SECRET_KEY=42e9e2483b4af92719ec4788a107bb70e53fac00386435e7982ecc984e87ae69

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--timeout", "600", "app:app"]