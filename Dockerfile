# Use Python 3.9 base image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Create directories for models and cache
RUN mkdir -p /models/torch_cache /models/silero

# Download Silero model
RUN python -c "import torch; torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_stt', language='en', device='cpu')"

# Copy the rest of the application code
COPY . .

# Expose port 3000 internally
EXPOSE 3000

# Command to run your Flask app (adjust if necessary)
CMD ["python", "webApp.py"]