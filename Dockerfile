# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for ffmpeg, libffi, libcurl, and espeak
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libffi-dev \
    libcurl4-openssl-dev \
    espeak \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Expose the port that the app runs on
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]