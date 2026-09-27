import os
import subprocess

def get_video_dimensions(video_path: str) -> tuple:
    """Helper to get video width and height using ffprobe."""
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-select_streams", "v:0", 
        "-show_entries", "stream=width,height", 
        "-of", "csv=s=x:p=0", 
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split('x'))
        return width, height
    except Exception as e:
        print(f"Error getting dimensions for {video_path}: {e}")
        return 1920, 1080 # Fallback

def center_crop_strategy(width: int, height: int) -> str:
    """
    Returns the FFmpeg crop filter string for a simple center crop to 9:16.
    Designed so this can be swapped out with OpenCV/MediaPipe later.
    """
    target_width = int(height * 9 / 16)
    x_offset = (width - target_width) // 2
    y_offset = 0
    return f"crop={target_width}:{height}:{x_offset}:{y_offset}"

def reframe_clips_to_vertical(clip_paths: list, output_dir: str = "vertical_output") -> list:
    """
    Takes a list of horizontal clips and crops them to 9:16 vertical using FFmpeg.
    Returns a list of paths to the vertical clips.
    """
    if not clip_paths:
        return []
        
    os.makedirs(output_dir, exist_ok=True)
    vertical_paths = []
    
    for i, clip_path in enumerate(clip_paths):
        base_name = os.path.basename(clip_path)
        # Keep same subfolder grouping as before
        parent_dir_name = os.path.basename(os.path.dirname(clip_path))
        
        video_output_dir = os.path.join(output_dir, parent_dir_name)
        os.makedirs(video_output_dir, exist_ok=True)
        
        vertical_clip_path = os.path.join(video_output_dir, f"vertical_{base_name}")
        
        if os.path.exists(vertical_clip_path):
            print(f"Vertical clip {base_name} already exists at {vertical_clip_path}, skipping.")
            vertical_paths.append(vertical_clip_path)
            continue
            
        print(f"Reframing {base_name} to vertical (9:16)...")
        
        width, height = get_video_dimensions(clip_path)
        crop_filter = center_crop_strategy(width, height)
        
        # We must re-encode the video here because we are applying a video filter (-vf)
        cmd = [
            "ffmpeg",
            "-y",
            "-i", clip_path,
            "-vf", crop_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "copy",
            vertical_clip_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            vertical_paths.append(vertical_clip_path)
        except subprocess.CalledProcessError as e:
            print(f"Error reframing clip {base_name}: {e}")
            
    print(f"Successfully reframed {len(vertical_paths)} clips.")
    return vertical_paths
