from moviepy import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips, AudioFileClip
import os
import random

    
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

    output_path = "/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/final_video.mp4"
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")