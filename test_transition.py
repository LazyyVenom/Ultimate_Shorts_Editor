from vid_editor.utils import create_video_transition
from moviepy import VideoFileClip

# Test video transition functionality
video_path1 = "testing_stuff/vid_1.mp4"
video_path2 = "testing_stuff/vid_2.mp4"

try:
    clip1 = VideoFileClip(video_path1).subclipped(0, 5)  # First 5 seconds
    clip2 = VideoFileClip(video_path2).subclipped(0, 5)  # First 5 seconds
    
    # Test fade transition
    transition_result = create_video_transition(clip1, clip2, transition_duration=1.0, transition_type="fade")
    
    output_path = "testing_stuff/vid_transition_test.mp4"
    transition_result.write_videofile(output_path, codec="h264", audio_codec="aac", bitrate="3000k", fps=30)
    
    clip1.close()
    clip2.close()
    transition_result.close()
    print(f"Video transition test saved to {output_path}")
    
except FileNotFoundError as e:
    print(f"Video file not found: {e}")
    print("Skipping transition test - need vid_2.mp4 file")
except Exception as e:
    print(f"Error during transition test: {e}")
