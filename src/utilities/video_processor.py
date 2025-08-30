from moviepy import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips, AudioFileClip, TextClip, vfx
from typing import List
import os
import random
import numpy as np
    
def add_primary_secondary_videos(primary_video: VideoFileClip, secondary_video: VideoFileClip, audio_duration: float) -> VideoFileClip:
    start_clip = primary_video.subclipped(0, 4)
    middle_clip_duration = audio_duration * random.uniform(0.3, 0.4)
    middle_clip = secondary_video.subclipped(0, middle_clip_duration)
    end_clip = primary_video.subclipped(4, audio_duration - middle_clip_duration)
    final_clip = concatenate_videoclips([start_clip, middle_clip, end_clip])
    return final_clip


def add_image_overlay(video: VideoFileClip, image_path: str, start_time: float, end_time: float, padding: int = 5) -> VideoFileClip:
    video_width, video_height = video.size
    
    max_width = video_width * (1 - padding / 100)
    max_height = video_height * (1 - padding / 100)
    
    image = ImageClip(image_path)
    
    img_width, img_height = image.size
    scale_width = max_width / img_width
    scale_height = max_height / img_height
    scale = min(scale_width, scale_height)
    
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    image = image.resized((new_width, new_height))
    
    duration = end_time - start_time
    image = image.with_duration(duration).with_start(start_time)

    center_x = (video_width - new_width) // 2
    center_y = (video_height - new_height) // 2
    bottom_y = video_height

    transition_duration = min(0.5, duration / 3)

    def position_function(t):
        """Calculate position based on time"""
        if t < transition_duration:
            progress = t / transition_duration
            progress = 1 - (1 - progress) ** 2
            y = bottom_y - (bottom_y - center_y) * progress
            return (center_x, y)
        elif t > (duration - transition_duration):
            progress = (t - (duration - transition_duration)) / transition_duration
            progress = progress ** 2
            y = center_y + (bottom_y - center_y) * progress
            return (center_x, y)
        else:
            return (center_x, center_y)
    
    image = image.with_position(position_function)
    
    final_video = CompositeVideoClip([video, image])
    
    return final_video

def add_captions(
    video,
    texts: List[str],
    start_times: List[float],
    durations: List[float],
    font_size: int = 60,
    color: str = "white",
    font: str = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/static/Utendo-Regular.ttf",
) -> CompositeVideoClip:
    clips = [video]
    for text, start_time, duration in zip(texts, start_times, durations):
        text_clip = TextClip(
            font=font,
            text=text,
            font_size=font_size,
            color=color,
            method="caption",
            size=video.size,
            duration=duration,
            text_align="center",
            # margin=(None, None, None, 120),
            stroke_color="black",
            stroke_width=15,
            vertical_align="center",
        ).with_start(start_time)
        clips.append(text_clip)

    video_with_text = CompositeVideoClip(clips)
    return video_with_text

def add_heading(
    video,
    text: str,
    font_size: int = 70,
    color: str = "white",
    font: str = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/static/Utendo-Bold.ttf",
    padding_top: int = 25,
    padding_side: int = 25,
    max_width_ratio: float = 0.9,
    stroke_color: str = "black",
    stroke_width: int = 8,
) -> CompositeVideoClip:
    """
    Add a static heading text to the video.
    """
    video_width, video_height = video.size
    
    # Calculate maximum text width
    max_text_width = int(video_width * max_width_ratio - 2 * padding_side)
    
    # Create text clip with automatic line wrapping
    heading_clip = TextClip(
        font=font,
        text=text,
        font_size=font_size,
        color=color,
        method="caption",
        size=(max_text_width, None),  # Let height be automatic
        text_align="center",
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    ).with_duration(video.duration)
    
    # Position the heading at the top center with padding
    x_position = (video_width - heading_clip.w) // 2
    y_position = padding_top
    
    heading_clip = heading_clip.with_position((x_position, y_position))
    
    # Combine video and heading
    video_with_heading = CompositeVideoClip([video, heading_clip])
    
    return video_with_heading

def add_smaller_captions(
    video,
    texts: List[str],
    start_times: List[float],
    end_times: List[float],
    font_size: int = 40,
    text_color: str = "white",
    bg_color: str = "black",
    bg_opacity: float = 0.7,
    font: str = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/static/Utendo-Regular.ttf",
    padding_bottom: int = 60,
    padding_horizontal: int = 40,
    bg_padding: int = 15,
) -> CompositeVideoClip:
    video_width, video_height = video.size
    clips = [video]
    
    for text, start_time, end_time in zip(texts, start_times, end_times):
        duration = end_time - start_time
        
        if duration <= 0:
            continue
        
        max_text_width = video_width - (2 * padding_horizontal)
        
        text_clip = TextClip(
            font=font,
            text=text,
            font_size=font_size,
            color=text_color,
            method="caption",
            size=(max_text_width, None),
            text_align="center",
        ).with_duration(duration).with_start(start_time)
        
        # Calculate background dimensions
        text_width, text_height = text_clip.size
        bg_width = text_width + (2 * bg_padding)
        bg_height = text_height + (2 * bg_padding)
        
        # Create background clip (semi-transparent rectangle)
        bg_clip = (ImageClip(np.full((bg_height, bg_width, 3), 
                                   [int(c) for c in _hex_to_rgb(bg_color)], 
                                   dtype=np.uint8))
                  .with_duration(duration)
                  .with_start(start_time)
                  .with_opacity(bg_opacity))
        
        # Position background at bottom center
        bg_x = (video_width - bg_width) // 2
        bg_y = video_height - padding_bottom - bg_height
        bg_clip = bg_clip.with_position((bg_x, bg_y))
        
        # Position text on top of background
        text_x = (video_width - text_width) // 2
        text_y = video_height - padding_bottom - bg_height + bg_padding
        text_clip = text_clip.with_position((text_x, text_y))
        
        # Add both background and text to clips
        clips.append(bg_clip)
        clips.append(text_clip)
    
    return CompositeVideoClip(clips)


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    # Handle common color names
    color_map = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
    }
    
    if hex_color.lower() in color_map:
        return color_map[hex_color.lower()]
    
    # Handle hex colors
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    elif len(hex_color) == 3:
        return tuple(int(hex_color[i]*2, 16) for i in range(3))
    else:
        return (0, 0, 0)  # Default to black if invalid

if __name__ == "__main__":
    primary_video_path = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/primary.mp4"
    secondary_video_path = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/secondary.mp4"
    audio_path = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/audio_processed.wav"

    primary_video = VideoFileClip(primary_video_path)
    secondary_video = VideoFileClip(secondary_video_path)
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    
    final_clip = add_primary_secondary_videos(primary_video, secondary_video, audio_duration)
    final_clip = final_clip.with_audio(audio_clip)

    image_path = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/img1.jpeg"
    final_clip = add_image_overlay(final_clip, image_path, start_time=2, end_time=audio_duration - 8, padding=10)

    # Add heading to the video
    heading_text = "Coding Till 20LPA Day 6"
    print("Adding heading to video...")
    final_clip = add_heading(
        final_clip,
        text=heading_text,
        font_size=65,
        color="white",
        padding_top=30,
        padding_side=20
    )

    from caption_processor import GenerateCaptions
    print("Generating captions...")
    caption_generator = GenerateCaptions(model_size="medium", device="cpu")
    caption_data = caption_generator.generate(audio_path)
    
    print(f"Generated {len(caption_data['captions'])} captions")
    print("Sample caption data:", {
        'captions': caption_data['captions'][:5],
        'start_times': caption_data['start_times'][:5],
        'durations': caption_data['durations'][:5]
    })
    
    print("Adding captions to video...")
    final_clip = add_captions(
        final_clip,
        texts=caption_data['captions'],
        start_times=caption_data['start_times'],
        durations=caption_data['durations'],
        color="white"
    )

    smaller_captions = [
        "Subscribe for more coding tips!",
        "Follow for daily updates.",
        "Share this video with friends."
    ]
    smaller_start_times = [3, 8, 14]
    smaller_end_times = [7, 12, 18]

    final_clip = add_smaller_captions(
        final_clip,
        texts=smaller_captions,
        start_times=smaller_start_times,
        end_times=smaller_end_times,
        font_size=38,
        text_color="white",
        bg_color="black",
        bg_opacity=0.7,
        padding_bottom=55,
        padding_horizontal=35,
        bg_padding=12,
    )

    output_path = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/final_video_with_captions.mp4"
    print(f"Writing final video with captions to: {output_path}")
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")