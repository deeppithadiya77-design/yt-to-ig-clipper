import whisper
import json
import os

def transcribe_video(video_path: str, output_dir: str = "transcripts", model_size: str = "base") -> str:
    """
    Transcribes the video using Whisper and extracts word-level timestamps.
    Saves the full transcript as JSON.
    Returns the path to the JSON transcript file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to JSON
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    json_path = os.path.join(output_dir, f"{base_name}_transcript.json")
    
    if os.path.exists(json_path):
        print(f"Transcript already exists at {json_path}, skipping transcription.")
        return json_path
        
    print(f"Loading Whisper model '{model_size}'...")
    # Whisper automatically falls back to CPU if GPU is not available
    model = whisper.load_model(model_size)
    
    print(f"Transcribing video: {video_path}...")
    # extract word-level timestamps
    result = model.transcribe(video_path, word_timestamps=True)
    
    # Structure the output nicely
    formatted_data = {
        "text": result["text"],
        "segments": []
    }
    
    for segment in result.get("segments", []):
        seg_data = {
            "start": segment.get("start"),
            "end": segment.get("end"),
            "text": segment.get("text"),
            "words": []
        }
        if "words" in segment:
            for word in segment["words"]:
                seg_data["words"].append({
                    "word": word.get("word"),
                    "start": word.get("start"),
                    "end": word.get("end")
                })
        formatted_data["segments"].append(seg_data)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=4, ensure_ascii=False)
        
    print(f"Transcription saved to {json_path}")
    return json_path
