#!/usr/bin/env python3
"""
Test specifically for text overlays to ensure they're appearing correctly
"""

import os
from vid_editor.utils import add_text_overlay, combine_videos

def test_text_overlays():
    """Test text overlays specifically"""
    
    print("📝 TESTING TEXT OVERLAYS")
    print("="*40)
    
    # Test files
    primary_video = "testing_stuff/vid_1.mp4"
    output_path = "testing_stuff/test_text_only.mp4"
    
    # Check if test files exist
    if not os.path.exists(primary_video):
        print(f"❌ Primary video not found: {primary_video}")
        return
    
    print(f"📹 Video: {primary_video}")
    print(f"📤 Output: {output_path}")
    print("="*40)
    
    try:
        # Load the video
        video = combine_videos(primary_video)
        print("✅ Video loaded successfully")
        
        # Add multiple text overlays at different times
        texts_and_times = [
            ("Hello World!", 1.0),
            ("Text at 3 seconds", 3.0),
            ("Final Text", 5.0)
        ]
        
        print("📝 Adding text overlays:")
        for text, timestamp in texts_and_times:
            print(f"   💬 '{text}' at {timestamp}s")
            video = add_text_overlay(video, text, timestamp, duration=2.0)
        
        print("✅ All text overlays added successfully")
        
        # Write the final video
        print("🎥 Rendering final video...")
        video.write_videofile(
            output_path, 
            codec="h264", 
            audio_codec="aac", 
            threads=4, 
            bitrate="3000k"
        )
        
        # Clean up
        video.close()
        
        print("="*40)
        print("🎉 SUCCESS! Text overlay test completed!")
        print(f"📁 Check the output: {output_path}")
        print("📝 You should see 3 text overlays appearing at different times")
        print("="*40)
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_text_overlays()
