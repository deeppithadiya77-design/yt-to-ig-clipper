import os
import yt_dlp

def download_video(url: str, output_dir: str = "downloads") -> str:
    """
    Downloads a YouTube video in the best quality mp4 format.
    Returns the absolute path to the downloaded video.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Template for yt-dlp output file
    outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'quiet': False,
        'no_warnings': False,
    }
    
    print(f"Downloading video from {url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # Prepare the expected output filename
        downloaded_file = ydl.prepare_filename(info_dict)
        
    print(f"Video downloaded successfully to {downloaded_file}")
    return downloaded_file
