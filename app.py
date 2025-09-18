from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid
import whisper
from transformers import pipeline
import yt_dlp

# Initialize FastAPI app
app = FastAPI(title="YouTube Transcriber & Summarizer")

# Load models (only once at startup)
transcriber = whisper.load_model("tiny")  # use "small" / "medium" for better accuracy
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Request body schema
class VideoRequest(BaseModel):
    url: str

def download_audio(youtube_url: str) -> str:
    """Download YouTube audio and return file path"""
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filename,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return filename

@app.post("/transcribe_and_summarize")
async def transcribe_and_summarize(req: VideoRequest):
    try:
        # Step 1: Download audio
        audio_path = download_audio(req.url)

        # Step 2: Transcribe audio
        result = transcriber.transcribe(audio_path)
        transcription = result["text"]

        # Step 3: Summarize (truncate if text too long)
        text_for_summary = transcription[:2000] if len(transcription) > 2000 else transcription
        summary = summarizer(text_for_summary, max_length=150, min_length=40, do_sample=False)[0]['summary_text']

        # Cleanup temp file
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {
            "transcription": transcription,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
  
