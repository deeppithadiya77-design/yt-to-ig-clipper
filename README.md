# YouTube to IG Clipper

A fully automated, local pipeline that takes a YouTube video URL and generates 3-5 vertical (9:16) clips ready to post on Instagram Reels or TikTok. It automatically identifies the most viral/engaging moments using AI, center-crops the video, and burns CapCut-style word-by-word animated captions directly into the final clips.

## Features

- **Automated Downloading:** Fetches the best quality video and audio directly from YouTube.
- **AI Transcription:** Uses OpenAI's Whisper model (running locally) to transcribe the video and extract word-level timestamps.
- **Viral Highlight Detection:** Uses the Gemini 2.5 Flash API to analyze the transcript and intelligently pick 3-5 engaging segments (30-60 seconds long).
- **Lightning Fast Clipping:** Losslessly slices the original video into clips using FFmpeg stream copying.
- **Vertical Reframing:** Center-crops horizontal videos into 9:16 vertical format.
- **Animated Captions:** Generates dynamic, word-by-word highlighted captions (ASS format) and burns them into the final videos.

## Tech Stack

- **Python 3** (Orchestration & Logic)
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** (Video Downloading)
- **[OpenAI Whisper](https://github.com/openai/whisper)** (Speech-to-Text & Timestamps)
- **[Google GenAI SDK](https://pypi.org/project/google-genai/)** (Highlight Detection via Gemini API)
- **[FFmpeg](https://ffmpeg.org/)** (Video Cropping, Slicing, and Caption Burning)

## Setup Instructions

### Prerequisites
- Python 3.9+
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to your system PATH.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/deeppithadiya77-design/yt-to-ig-clipper.git
   cd yt-to-ig-clipper
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the Gemini API Key:**
   - Create a file named `.env` in the root of the project folder.
   - You MUST add your Gemini API key to this file for the highlight detection to work:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the pipeline from your terminal by passing a public YouTube URL to `main.py`:

```bash
python main.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

### The pipeline will run through 6 automated steps:
1. `downloads/`: Saves the full raw video.
2. `transcripts/`: Saves the raw JSON transcript from Whisper.
3. `highlights/`: Saves the JSON highlight timestamps returned by Gemini.
4. `output/`: Saves the raw, uncut horizontal clips.
5. `vertical_output/`: Saves the clips center-cropped to 9:16.
6. `final_output/`: Saves the finalized clips with burned-in captions!

Check the `final_output/` folder when the script finishes for your ready-to-post videos!
