import os
from moviepy import AudioFileClip, TextClip, CompositeVideoClip, VideoFileClip, vfx

def add_heading(video: VideoFileClip, heading: str) -> CompositeVideoClip:
    text_clip = TextClip(
        text=heading,
        font=r"static/Utendo-Bold.ttf",
        font_size=57,
        color='white',
        bg_color='black',
        size=(video.size[0], None),
        duration=video.duration,
        text_align="center",
        margin=(None, 25),
        method="caption",
        interline=25,
        vertical_align="top",
    ).with_start(0)

    fade_duration = min(1, video.duration / 5)
    text_clip = text_clip.with_effects([vfx.SlideIn(fade_duration, 'top'), vfx.SlideOut(fade_duration, 'top')])

    video_with_text = CompositeVideoClip([video, text_clip])
    return video_with_text