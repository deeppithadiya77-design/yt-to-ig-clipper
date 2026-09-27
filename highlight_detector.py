import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List

class Highlight(BaseModel):
    start_time: float
    end_time: float
    reason: str

class HighlightResponse(BaseModel):
    highlights: List[Highlight]

def detect_highlights(transcript_path: str, output_dir: str = "highlights") -> str:
    """
    Uses Gemini API to detect 3-5 engaging highlights from the transcript.
    Returns the path to the highlights JSON file.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Valid GEMINI_API_KEY not found in environment variables or .env file.")
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the highlights
    base_name = os.path.basename(transcript_path).replace("_transcript.json", "")
    output_path = os.path.join(output_dir, f"{base_name}_highlights.json")
    
    if os.path.exists(output_path):
        print(f"Highlights already exist at {output_path}, skipping detection.")
        return output_path
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
        
    # Prepare transcript with timestamps for Gemini
    formatted_transcript = ""
    for segment in transcript_data.get("segments", []):
        start = segment.get("start")
        end = segment.get("end")
        text = segment.get("text", "").strip()
        formatted_transcript += f"[{start:.1f}s - {end:.1f}s]: {text}\n"
    
    prompt = f"""
    You are an expert social media manager and video editor. Your task is to identify the 3 to 5 most engaging, viral-worthy segments from the following video transcript. 
    Each segment should be roughly between 30 and 60 seconds long.
    
    For each segment, provide the precise start_time and end_time (in seconds) based on the provided timestamps, and a short reason why the segment is engaging.
    
    Transcript:
    {formatted_transcript}
    """
    
    print("Calling Gemini API for highlight detection...")
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=HighlightResponse,
        ),
    )
    
    # Parse the response to ensure it matches schema, then write properly
    with open(output_path, 'w', encoding='utf-8') as f:
        # Since response.text is guaranteed to be JSON matching the schema
        # We can write it directly or load/dump to pretty print
        try:
            parsed_json = json.loads(response.text)
            json.dump(parsed_json, f, indent=4, ensure_ascii=False)
        except json.JSONDecodeError:
            # Fallback to direct text write
            f.write(response.text)
            
    print(f"Highlights saved to {output_path}")
    return output_path
