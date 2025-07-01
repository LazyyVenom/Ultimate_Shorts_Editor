from editor.utils import add_heading
from moviepy import VideoFileClip

video_path = "testing_stuff/vid_1.mp4"
video = VideoFileClip(video_path)
heading = "Coding Till 20LPA Day 8"
video_with_heading = add_heading(video, heading)
output_path = "testing_stuff/vid_1_with_heading.mp4"
video_with_heading.write_videofile(output_path, codec="h264", audio_codec="aac", bitrate="3000k", fps=30)  # Adjust bitrate as needed
video.close()
video_with_heading.close()
print(f"Video with heading saved to {output_path}")

