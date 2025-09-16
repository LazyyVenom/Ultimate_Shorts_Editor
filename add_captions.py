import argparse
import os
import sys
from moviepy import ColorClip, AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utilities.caption_processor import GenerateCaptions
from utilities.video_processor import add_captions

def create_captions_video(audio_path: str, output_path: str):
    """
    Generates a video with captions on a green background from an audio file.

    Args:
        audio_path (str): Path to the input audio file.
        output_path (str): Path to save the output video file.
    """
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return

    print("1. Loading audio and getting duration...")
    audio_clip = AudioFileClip(audio_path)
    video_duration = audio_clip.duration
    print(f"   - Audio duration: {video_duration:.2f} seconds")

    print("2. Generating captions...")
    try:
        caption_generator = GenerateCaptions(model_size="medium", device="cpu")
        caption_data = caption_generator.generate(audio_path)
        print(f"   - Generated {len(caption_data['captions'])} caption segments.")
    except Exception as e:
        print(f"Error during caption generation: {e}")
        return

    print("3. Creating green background video...")
    # Standard green screen color
    green_screen_color = [0, 255, 0]
    video_size = (1080, 1920)  # 9:16 aspect ratio for shorts

    background_clip = ColorClip(size=video_size, color=green_screen_color, duration=video_duration)

    print("4. Adding captions to the video...")
    try:
        video_with_captions = add_captions(
            background_clip,
            texts=caption_data['captions'],
            start_times=caption_data['start_times'],
            durations=caption_data['durations'],
            color="white"
        )
        print("   - Captions added successfully.")
    except Exception as e:
        print(f"Error adding captions to video: {e}")
        return

    # The final clip should be a CompositeVideoClip with the background and captions
    # The add_captions function should return a CompositeVideoClip
    final_clip = video_with_captions

    print(f"5. Exporting video to {output_path}...")
    try:
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            ffmpeg_params=["-crf", "18"]
        )
        print("   - Video exported successfully!")
    except Exception as e:
        print(f"Error exporting video: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a captions video on a green screen from an audio file.")
    parser.add_argument("audio_path", type=str, help="Path to the input audio file.")
    parser.add_argument("output_path", type=str, help="Path to save the output MP4 video.")
    
    args = parser.parse_args()

    create_captions_video(args.audio_path, args.output_path)
