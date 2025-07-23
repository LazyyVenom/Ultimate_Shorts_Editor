from vid_editor.utils import add_image_overlay, combine_videos
from moviepy import VideoFileClip

# Test video processing with image overlay
video_path = "testing_stuff/vid_1.mp4"
image_path = "testing_stuff/img_1.jpeg"

video = VideoFileClip(video_path)
video_with_image = add_image_overlay(video, image_path, 2.0, 3.0)  # Add image at 2s for 3s duration

output_path = "testing_stuff/vid_with_image_test.mp4"
video_with_image.write_videofile(output_path, codec="h264", audio_codec="aac", bitrate="3000k", fps=30)

video.close()
video_with_image.close()
print(f"Video with image overlay saved to {output_path}")
