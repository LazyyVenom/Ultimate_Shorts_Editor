from moviepy import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips, AudioFileClip
import os
import random

    
def add_primary_secondary_videos(primary_video: VideoFileClip, secondary_video: VideoFileClip, audio_duration: float) -> VideoFileClip:
    # Dividing Primary video into two parts
    total_duration = 4
    start_clip = primary_video.subclipped(0, 4)
    middle_clip_duration = audio_duration * random.uniform(0.3, 0.4)
    total_duration += middle_clip_duration
    total_duration += audio_duration - middle_clip_duration
    print("Total Duration: ", total_duration)
    print("Audio Duration: ", audio_duration)
    middle_clip = secondary_video.subclipped(0, middle_clip_duration)

    end_clip = primary_video.subclipped(4, audio_duration - middle_clip_duration)
    final_clip = concatenate_videoclips([start_clip, middle_clip, end_clip])
    return final_clip


if __name__ == "__main__":
    primary_video_path = "sample_data/videos/primary.mp4"
    secondary_video_path = "sample_data/videos/secondary.mp4"
    audio_path = "testing_stuff/New Recording-enhanced-v2.wav"

    primary_video = VideoFileClip(primary_video_path)
    secondary_video = VideoFileClip(secondary_video_path)
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    
    final_clip = add_primary_secondary_videos(primary_video, secondary_video, audio_duration)
    final_clip = final_clip.set_audio(audio_clip)
    output_path = "output/final_video.mp4"
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")