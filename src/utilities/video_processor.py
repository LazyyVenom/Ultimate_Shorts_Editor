from moviepy import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips, AudioFileClip, TextClip, vfx
from typing import List
import os
import random
import numpy as np
    
def add_primary_secondary_videos(primary_video: VideoFileClip, secondary_video: VideoFileClip, audio_duration: float) -> VideoFileClip:
    """Combine primary and secondary videos with improved stability"""
    try:
        # Ensure we don't exceed available video durations
        primary_duration = primary_video.duration
        secondary_duration = secondary_video.duration
        
        print(f"Primary video duration: {primary_duration:.2f}s")
        print(f"Secondary video duration: {secondary_duration:.2f}s")
        print(f"Required audio duration: {audio_duration:.2f}s")
        
        # Use a simpler approach - just switch between videos at logical points
        if primary_duration >= audio_duration:
            # Primary video is long enough, just use it
            return primary_video.subclipped(0, audio_duration)
        
        # Create segments with better bounds checking
        segments = []
        current_time = 0
        
        # Start with primary video (first 4 seconds or available duration)
        start_duration = min(4, primary_duration, audio_duration)
        if start_duration > 0:
            segments.append(primary_video.subclipped(0, start_duration))
            current_time += start_duration
        
        # Fill remaining time with secondary video if available
        if current_time < audio_duration and secondary_duration > 0:
            remaining_duration = audio_duration - current_time
            secondary_clip_duration = min(remaining_duration, secondary_duration)
            if secondary_clip_duration > 0:
                segments.append(secondary_video.subclipped(0, secondary_clip_duration))
                current_time += secondary_clip_duration
        
        # If we still need more time and have more primary video, use it
        if current_time < audio_duration and primary_duration > start_duration:
            remaining_duration = audio_duration - current_time
            available_primary = primary_duration - start_duration
            final_clip_duration = min(remaining_duration, available_primary)
            if final_clip_duration > 0:
                segments.append(primary_video.subclipped(start_duration, start_duration + final_clip_duration))
        
        # Concatenate segments if we have more than one
        if len(segments) > 1:
            return concatenate_videoclips(segments)
        elif len(segments) == 1:
            return segments[0]
        else:
            # Fallback to primary video
            return primary_video.subclipped(0, min(primary_duration, audio_duration))
            
    except Exception as e:
        print(f"Error in add_primary_secondary_videos: {e}")
        # Fallback to just primary video
        try:
            return primary_video.subclipped(0, min(primary_video.duration, audio_duration))
        except:
            return primary_video


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
    """Add captions with better error handling"""
    try:
        clips = [video]
        
        # Validate font file
        if not os.path.exists(font):
            print(f"Warning: Font file {font} not found, using default")
            font = None
        
        for text, start_time, duration in zip(texts, start_times, durations):
            try:
                # Validate inputs
                if not text or not text.strip():
                    continue
                if duration <= 0:
                    continue
                if start_time < 0:
                    start_time = 0
                
                # Create text clip with error handling
                text_clip_params = {
                    "text": text.strip(),
                    "font_size": max(10, font_size),
                    "color": color,
                    "method": "caption",
                    "size": video.size,
                    "duration": duration,
                    "text_align": "center",
                    "stroke_color": "black",
                    "stroke_width": 15,
                    "vertical_align": "center",
                }
                
                if font:
                    text_clip_params["font"] = font
                
                text_clip = TextClip(**text_clip_params).with_start(start_time)
                clips.append(text_clip)
                
            except Exception as e:
                print(f"Error creating caption '{text[:20]}...': {e}")
                continue

        if len(clips) == 1:
            # No captions were added successfully
            return video
            
        video_with_text = CompositeVideoClip(clips)
        return video_with_text
        
    except Exception as e:
        print(f"Error in add_captions: {e}")
        return video

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
    Add a static heading text to the video with error handling.
    """
    try:
        if not text or not text.strip():
            print("Warning: Empty heading text")
            return video
            
        video_width, video_height = video.size
        
        # Validate font file
        if not os.path.exists(font):
            print(f"Warning: Font file {font} not found, using default")
            font = None
        
        # Calculate maximum text width
        max_text_width = int(video_width * max_width_ratio - 2 * padding_side)
        if max_text_width <= 0:
            max_text_width = video_width // 2
        
        # Create text clip with automatic line wrapping
        heading_params = {
            "text": text.strip(),
            "font_size": max(10, font_size),
            "color": color,
            "method": "caption",
            "size": (max_text_width, None),  # Let height be automatic
            "text_align": "center",
            "stroke_color": stroke_color,
            "stroke_width": max(0, stroke_width),
        }
        
        if font:
            heading_params["font"] = font
            
        heading_clip = TextClip(**heading_params).with_duration(video.duration)
        
        # Position the heading at the top center with padding
        x_position = max(0, (video_width - heading_clip.w) // 2)
        y_position = max(0, padding_top)
        
        # Ensure heading doesn't go off screen
        if y_position + heading_clip.h > video_height:
            y_position = max(0, video_height - heading_clip.h)
        
        heading_clip = heading_clip.with_position((x_position, y_position))
        
        # Combine with video
        final_video = CompositeVideoClip([video, heading_clip])
        return final_video
        
    except Exception as e:
        print(f"Error in add_heading: {e}")
        return video


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
    """Add smaller captions with background at bottom of video with error handling"""
    try:
        video_width, video_height = video.size
        clips = [video]
        
        # Validate font file
        if not os.path.exists(font):
            print(f"Warning: Font file {font} not found, using default")
            font = None
        
        for text, start_time, end_time in zip(texts, start_times, end_times):
            try:
                duration = end_time - start_time
                
                if duration <= 0 or not text or not text.strip():
                    continue
                
                if start_time < 0:
                    start_time = 0
                
                max_text_width = max(100, video_width - (2 * padding_horizontal))
                
                # Create text clip with error handling
                text_params = {
                    "text": text.strip(),
                    "font_size": max(10, font_size),
                    "color": text_color,
                    "method": "caption",
                    "size": (max_text_width, None),
                    "text_align": "center",
                }
                
                if font:
                    text_params["font"] = font
                
                text_clip = TextClip(**text_params).with_duration(duration).with_start(start_time)
                
                # Calculate background dimensions
                text_width, text_height = text_clip.size
                bg_width = text_width + (2 * bg_padding)
                bg_height = text_height + (2 * bg_padding)
                
                # Create background clip (semi-transparent rectangle)
                try:
                    bg_color_rgb = _hex_to_rgb(bg_color)
                    bg_array = np.full((bg_height, bg_width, 3), bg_color_rgb, dtype=np.uint8)
                    
                    bg_clip = (ImageClip(bg_array)
                              .with_duration(duration)
                              .with_start(start_time)
                              .with_opacity(max(0.1, min(1.0, bg_opacity))))
                    
                    # Position background at bottom center
                    bg_x = max(0, (video_width - bg_width) // 2)
                    bg_y = max(0, video_height - padding_bottom - bg_height)
                    bg_clip = bg_clip.with_position((bg_x, bg_y))
                    
                    # Position text on top of background
                    text_x = max(0, (video_width - text_width) // 2)
                    text_y = max(0, video_height - padding_bottom - bg_height + bg_padding)
                    text_clip = text_clip.with_position((text_x, text_y))
                    
                    # Add both background and text to clips
                    clips.append(bg_clip)
                    clips.append(text_clip)
                    
                except Exception as e:
                    print(f"Error creating background for caption '{text[:20]}...': {e}")
                    # Add just the text without background
                    text_x = max(0, (video_width - text_clip.w) // 2)
                    text_y = max(0, video_height - padding_bottom - text_clip.h)
                    text_clip = text_clip.with_position((text_x, text_y))
                    clips.append(text_clip)
                    
            except Exception as e:
                print(f"Error adding smaller caption '{text[:20]}...': {e}")
                continue
        
        if len(clips) == 1:
            # No captions were added successfully
            return video
            
        return CompositeVideoClip(clips)
        
    except Exception as e:
        print(f"Error in add_smaller_captions: {e}")
        return video


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