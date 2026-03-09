# 1. Use a Python 3.11 base image
FROM python:3.11-slim

# 2. Install system dependencies for Audio, FFmpeg, and Speech
# We need espeak and libasound2 for the voice engine to work inside the container
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak \
    libasound2-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /app

# 4. Copy your requirements file first (to cache the layer)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your main script
COPY main.py .

# 7. Expose Streamlit's default port
EXPOSE 8501

# 8. Set environment variables to prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# 9. Run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0"]
