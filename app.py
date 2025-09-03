import os
import tempfile
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from yt_dlp import YoutubeDL

from faster_whisper import WhisperModel

DEFAULT_MODEL = os.getenv("WHISPER_MODEL", "tiny")  
DEVICE = os.getenv("WHISPER_DEVICE", "auto")      
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8_float16") 
# Load model once at startup for faster requests
model = WhisperModel(DEFAULT_MODEL, device=DEVICE, compute_type=COMPUTE_TYPE)

app = FastAPI(title="YouTube Transcriber API", version="1.0.0")

# CORS (open by default; tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscribeRequest(BaseModel):
    url: HttpUrl
    task: Optional[str] = "transcribe"  
    language: Optional[str] = None      
    vad_filter: Optional[bool] = True  

class Segment(BaseModel):
    start: float
    end: float
    text: str

class TranscribeResponse(BaseModel):
    text: str
    language: str
    duration: float
    segments: List[Segment]

@app.get("/health")
def health():
    return {"status": "ok", "model": DEFAULT_MODEL, "device": DEVICE, "compute_type": COMPUTE_TYPE}

def _download_audio_to(temp_dir: str, url: str) -> str:
    """
    Download best audio using yt-dlp and convert/extract to mp3 via ffmpeg.
    Returns the audio file path.
    """
    outtmpl = os.path.join(temp_dir, "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "nocheckcertificate": True,
        "noprogress": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Compute produced mp3 path
        vid = info.get("id")
        audio_path = os.path.join(temp_dir, f"{vid}.mp3")
        if not os.path.exists(audio_path):
            # Fallback to original ext if postprocessor didn't run
            ext = info.get("ext", "m4a")
            fallback = os.path.join(temp_dir, f"{vid}.{ext}")
            if os.path.exists(fallback):
                return fallback
            raise FileNotFoundError("Audio file not found after download.")
        return audio_path

@app.post("/transcribe", response_model=TranscribeResponse)
def transcribe(req: TranscribeRequest):
    """
    Provide a YouTube URL and receive the full transcript + segments.
    """
    if req.task not in {"transcribe", "translate"}:
        raise HTTPException(status_code=400, detail="task must be 'transcribe' or 'translate'")

    with tempfile.TemporaryDirectory() as td:
        try:
            audio_path = _download_audio_to(td, str(req.url))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to download audio: {e}")

        try:
            # Run transcription
            segments, info = model.transcribe(
                audio_path,
                task=req.task,
                language=req.language,
                vad_filter=req.vad_filter,
                vad_parameters=dict(min_silence_duration_ms=500),
                beam_size=5,
                best_of=5,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

        all_segments = []
        full_text_parts = []
        duration = float(info.duration) if hasattr(info, "duration") else 0.0
        detected_language = getattr(info, "language", None) or req.language or "unknown"

        for seg in segments:
            seg_text = seg.text.strip()
            all_segments.append(Segment(start=float(seg.start), end=float(seg.end), text=seg_text))
            full_text_parts.append(seg_text)

        return TranscribeResponse(
            text=" ".join(full_text_parts).strip(),
            language=detected_language,
            duration=duration,
            segments=all_segments,
        )
