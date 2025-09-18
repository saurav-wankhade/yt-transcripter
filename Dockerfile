# Dockerfile
FROM python:3.11-slim


# Set working directory
WORKDIR /app


# System dependencies for yt-dlp, pydub (ffmpeg)
RUN apt-get update && apt-get install -y \
ffmpeg \
git \
&& rm -rf /var/lib/apt/lists/*


# Upgrade pip and install requirements
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
&& pip install -r requirements.txt


# Copy application code
COPY . .


# Expose FastAPI port
EXPOSE 8000


# Run the app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
