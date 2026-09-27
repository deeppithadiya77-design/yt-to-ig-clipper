import os
import json
import subprocess

def cut_clips(video_path: str, highlights_path: str, output_dir: str = "output") -> list:
    """
    Cuts the video into smaller clips based on the highlights JSON using FFmpeg.
    Returns a list of paths to the generated clips.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    with open(highlights_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    highlights = data.get("highlights", [])
    if not highlights:
        print("No highlights found to cut.")
        return []
        
    clip_paths = []
    
    # Group clips by video name to keep output organized
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_dir = os.path.join(output_dir, base_name)
    os.makedirs(video_output_dir, exist_ok=True)
    
    for i, highlight in enumerate(highlights):
        start_time = highlight.get("start_time")
        end_time = highlight.get("end_time")
        duration = end_time - start_time
        
        clip_name = f"clip_{i+1}.mp4"
        clip_path = os.path.join(video_output_dir, clip_name)
        
        if os.path.exists(clip_path):
            print(f"Clip {clip_name} already exists at {clip_path}, skipping.")
            clip_paths.append(clip_path)
            continue
            
        print(f"Cutting {clip_name} (from {start_time}s to {end_time}s)...")
        
        # FFmpeg command to cut video
        # -ss seeks to start_time
        # -i input
        # -t sets duration
        # -c:v copy and -c:a copy means we avoid re-encoding for lightning speed cuts
        cmd = [
            "ffmpeg",
            "-y", # Overwrite if exists
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(duration),
            "-c:v", "copy",
            "-c:a", "copy",
            clip_path
        ]
        
        try:
            # We redirect stdout/stderr to avoid polluting the terminal
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            clip_paths.append(clip_path)
        except subprocess.CalledProcessError as e:
            print(f"Error cutting clip {i+1}: {e}")
            
    print(f"Successfully cut {len(clip_paths)} clips and saved them to {video_output_dir}")
    return clip_paths
