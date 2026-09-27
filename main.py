import argparse
from downloader import download_video
from transcriber import transcribe_video
from highlight_detector import detect_highlights
from clipper import cut_clips
from reframer import reframe_clips_to_vertical
from caption_burner import burn_captions

def main():
    parser = argparse.ArgumentParser(description="YouTube to Instagram Clipping Tool")
    parser.add_argument("url", help="YouTube video URL")
    args = parser.parse_args()

    print("=== YouTube to IG Clipper ===")
    
    # STEP 1 - Download
    try:
        video_path = download_video(args.url)
        print(f"Step 1 Complete. Video saved at: {video_path}\n")
    except Exception as e:
        print(f"Error during download: {e}")
        return

    # STEP 2 - Transcribe
    try:
        transcript_path = transcribe_video(video_path)
        print(f"Step 2 Complete. Transcript saved at: {transcript_path}\n")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return

    # STEP 3 - Highlight Detection
    try:
        highlights_path = detect_highlights(transcript_path)
        print(f"Step 3 Complete. Highlights saved at: {highlights_path}\n")
    except Exception as e:
        print(f"Error during highlight detection: {e}")
        return

    # STEP 4 - Cut Clips
    try:
        clip_paths = cut_clips(video_path, highlights_path)
        print(f"Step 4 Complete. Cut {len(clip_paths)} clips.\n")
    except Exception as e:
        print(f"Error during clip cutting: {e}")
        return

    # STEP 5 - Reframe to Vertical
    try:
        vertical_paths = reframe_clips_to_vertical(clip_paths)
        print(f"Step 5 Complete. Reframed {len(vertical_paths)} clips to vertical.\n")
    except Exception as e:
        print(f"Error during reframing: {e}")
        return

    # STEP 6 - Burn Captions
    try:
        final_paths = burn_captions(vertical_paths, highlights_path, transcript_path)
        print(f"Step 6 Complete. Final clips with burned captions saved!\n")
        print("Pipeline Complete! Check the 'final_output' folder.")
    except Exception as e:
        print(f"Error during caption burning: {e}")
        return

if __name__ == "__main__":
    main()
