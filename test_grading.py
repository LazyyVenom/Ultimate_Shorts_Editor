from vid_editor.utils import apply_color_grading
from moviepy import VideoFileClip

# Test color grading functionality
video_path = "testing_stuff/vid_1.mp4"

video = VideoFileClip(video_path)
video_graded = apply_color_grading(video, "warm")  # Apply warm color grading

output_path = "testing_stuff/vid_color_graded_test.mp4"
video_graded.write_videofile(output_path, codec="h264", audio_codec="aac", bitrate="3000k", fps=30)

video.close()
video_graded.close()
print(f"Video with color grading saved to {output_path}")
