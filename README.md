# 🎙️ YouTube Transcriber & Summarizer API

A FastAPI-based service that:
- Downloads audio from a YouTube video
- Transcribes it using [OpenAI Whisper](https://github.com/openai/whisper)
- Summarizes the transcription using [Hugging Face Transformers](https://huggingface.co/facebook/bart-large-cnn)

---

## 🚀 Features
- Input: YouTube video URL
- Output: JSON with full transcription + concise summary
- Interactive API docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📦 Requirements

- Python 3.11
- [FFmpeg](https://ffmpeg.org/download.html) (must be installed and in PATH)

Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg -y

# Windows (Chocolatey)
choco install ffmpeg


🔧 Setup

Clone this repository:

git clone https://github.com/saurav-wankhade/yt-transcripter.git
cd yt-transcripter


Create and activate a virtual environment:

python3.11 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows


Install dependencies:

pip install -r requirements.txt

▶️ Run the API

Start the FastAPI server:

uvicorn app:app --reload


On startup, you’ll see:

📌 Open the API docs here: http://127.0.0.1:8000/docs

📘 Usage

1. Go to http://127.0.0.1:8000/docs
2. Use the /transcribe_and_summarize endpoint
Input:

{
  "url": "https://www.youtube.com/watch?v=your_video_id"
}

Output:

{
  "transcription": "Full transcription of the video...",
  "summary": "Concise summary of the content..."
}

🛠 Tech Stack

FastAPI
Uvicorn
yt-dlp
Whisper
Transformers

⚠️ Notes
Hugging Face models may require a free access token
 if you hit rate limits.
Whisper can be slow on CPU. For faster performance, run with GPU + CUDA.