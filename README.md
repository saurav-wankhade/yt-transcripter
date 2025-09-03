# YouTube Transcriber (FastAPI + Python)

A tiny API service that downloads a YouTube video's audio and transcribes it locally using [faster-whisper](https://github.com/guillaumekln/faster-whisper).

> **Heads-up:** You need **FFmpeg** installed on your system (yt-dlp uses it to extract audio).

## Quickstart

```bash
# 1) Create & activate a venv (recommended)
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# 2) Install system dependency (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y ffmpeg

# 3) Install Python deps
pip install -r requirements.txt

# 4) (Optional) Choose a model — tiny/base/small/medium/large-v3
export WHISPER_MODEL=tiny
# You can also tweak device & compute type:
# export WHISPER_DEVICE=auto   # "auto", "cpu", or "cuda"
# export WHISPER_COMPUTE_TYPE=int8_float16  # "int8", "float16", "float32", etc.

# 5) Run the API
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Open: http://localhost:8000/docs to try it out.

## Usage

**POST** `/transcribe`

Request body (JSON):
```json
{
  "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
  "task": "transcribe",
  "language": null,
  "vad_filter": true
}
```

- `task`: `"transcribe"` keeps original language. `"translate"` outputs English.
- `language`: force language code (e.g., `"en"`, `"hi"`).
- `vad_filter`: enable voice activity detection to reduce noise.

Response:
```json
{
  "text": "Full transcript here...",
  "language": "en",
  "duration": 123.45,
  "segments": [
    {"start": 0.0, "end": 3.1, "text": "Hello everyone..."},
    ...
  ]
}
```

## Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

# Configure model (override at runtime)
ENV WHISPER_MODEL=tiny
ENV WHISPER_DEVICE=auto
ENV WHISPER_COMPUTE_TYPE=int8_float16

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build & run:
```bash
docker build -t yt-transcriber .
docker run --rm -it -p 8000:8000 yt-transcriber
```

## Notes

- First run downloads the Whisper model. Subsequent runs are much faster.
- `tiny` is fastest but less accurate; `small` or `medium` improves quality.
- For NVIDIA GPUs in Docker, run with `--gpus all` and set `WHISPER_DEVICE=cuda`.
