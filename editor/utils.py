import os
from moviepy import AudioFileClip, TextClip, CompositeVideoClip, VideoFileClip

def add_heading(video : VideoFileClip , heading : str) -> CompositeVideoClip:
    text_clip = TextClip(
            font=r"static/Utendo-Regular.ttf",
            text=heading,
            font_size=90,
            color='black',
            size=video.size,
            duration=video.duration,
            text_align="center",
            margin=(None, 50),
            stroke_color="white",
            stroke_width=10,
            vertical_align="top",
        ).with_start(0)
    # Removed the incorrect line
    video_with_text = CompositeVideoClip([video, text_clip])
    return video_with_text