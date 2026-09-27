import os
import json
import subprocess

def create_ass_file(clip_idx: int, clip_start: float, clip_end: float, transcript_data: dict, output_dir: str) -> str:
    """
    Creates an ASS subtitle file for a specific clip with word-by-word highlight styling.
    """
    ass_path = os.path.join(output_dir, f"captions_{clip_idx}.ass")
    
    # Extract words that fall within this clip's time window
    clip_words = []
    for segment in transcript_data.get("segments", []):
        for word_info in segment.get("words", []):
            w_start = word_info.get("start", 0)
            w_end = word_info.get("end", 0)
            word_text = word_info.get("word", "").strip()
            
            if not word_text:
                continue
                
            # If the word is at least partially in the clip
            if w_end > clip_start and w_start < clip_end:
                # Adjust timestamps relative to clip start
                rel_start = max(0, w_start - clip_start)
                rel_end = min(clip_end - clip_start, w_end - clip_start)
                clip_words.append({
                    "word": word_text,
                    "start": rel_start,
                    "end": rel_end
                })
                
    # ASS Header
    # PlayResX/Y matches our vertical 9:16 target (1080x1920)
    # Alignment 5 means center of the screen, MarginV=960 puts it exactly in the middle.
    # Alternatively, Alignment 8 (top center) or 2 (bottom center) with margin. We'll use 5 (center-center)
    ass_content = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 1",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: IGStyle,Arial,75,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,3,5,30,30,960,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    
    # Helper to convert seconds to ASS time format (H:MM:SS.cs)
    def to_ass_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h}:{m:02d}:{s:05.2f}"
        
    # Group words into short lines (e.g., max 5 words per line)
    words_per_line = 5
    lines = []
    for i in range(0, len(clip_words), words_per_line):
        lines.append(clip_words[i:i+words_per_line])
        
    for line in lines:
        if not line: continue
        
        # Duplicate the line for each word to create the word-by-word highlight effect
        for i, target_word in enumerate(line):
            t_start = target_word["start"]
            t_end = target_word["end"]
            
            styled_text = ""
            for j, w in enumerate(line):
                # &H0000FFFF is yellow in ASS BGR format
                if j == i:
                    styled_text += f"{{\\c&H00FFFF&}}{w['word']}{{\\c&HFFFFFF&}} "
                else:
                    styled_text += f"{w['word']} "
            styled_text = styled_text.strip()
            
            start_str = to_ass_time(t_start)
            end_str = to_ass_time(t_end)
            ass_content.append(f"Dialogue: 0,{start_str},{end_str},IGStyle,,0,0,0,,{styled_text}")
            
    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(ass_content))
        
    return ass_path

def burn_captions(vertical_paths: list, highlights_path: str, transcript_path: str, output_dir: str = "final_output") -> list:
    """
    Creates an ASS subtitle file for each clip and burns it into the vertical video using FFmpeg.
    """
    if not vertical_paths:
        return []
        
    os.makedirs(output_dir, exist_ok=True)
    
    with open(highlights_path, 'r', encoding='utf-8') as f:
        highlights_data = json.load(f)
    highlights = highlights_data.get("highlights", [])
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
        
    final_paths = []
    
    for i, clip_path in enumerate(vertical_paths):
        if i >= len(highlights):
            break
            
        highlight = highlights[i]
        clip_start = highlight.get("start_time")
        clip_end = highlight.get("end_time")
        
        base_name = os.path.basename(clip_path).replace("vertical_", "")
        parent_dir_name = os.path.basename(os.path.dirname(clip_path))
        
        video_output_dir = os.path.join(output_dir, parent_dir_name)
        os.makedirs(video_output_dir, exist_ok=True)
        
        final_clip_path = os.path.join(video_output_dir, f"final_{base_name}")
        
        if os.path.exists(final_clip_path):
            print(f"Final clip {base_name} already exists at {final_clip_path}, skipping.")
            final_paths.append(final_clip_path)
            continue
            
        print(f"Burning captions for {base_name}...")
        
        # 1. Create ASS file
        ass_path = create_ass_file(i+1, clip_start, clip_end, transcript_data, video_output_dir)
        
        # Safely escape backslashes for FFmpeg filters on Windows
        # Use relative path since absolute path with drive letter can confuse the ass filter parsing
        safe_ass_path = os.path.relpath(ass_path).replace('\\', '\\\\').replace(':', '\\:')
        
        # 2. Burn using FFmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-i", clip_path,
            "-vf", f"ass='{safe_ass_path}'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "copy",
            final_clip_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            final_paths.append(final_clip_path)
        except subprocess.CalledProcessError as e:
            print(f"Error burning captions on {base_name}: {e}")
            
    print(f"Successfully burned captions for {len(final_paths)} clips.")
    return final_paths
