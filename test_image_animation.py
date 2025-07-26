#!/usr/bin/env python3
"""
Test script for the new image overlay animation effect
Demonstrates images sliding up from bottom and sliding down on exit
"""

import os
from vid_editor.utils import add_image_overlay, combine_videos

def test_image_animation():
    """Test the new slide-up/slide-down image overlay animation"""
    
    # Test files
    primary_video = "testing_stuff/vid_1.mp4"
    test_image = "testing_stuff/img_1.jpeg"
    output_path = "testing_stuff/test_image_animation.mp4"
    
    # Check if test files exist
    if not os.path.exists(primary_video):
        print(f"❌ Primary video not found: {primary_video}")
        return
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return
    
    print("🎬 Testing Image Animation Effects...")
    print("="*50)
    print(f"📹 Video: {primary_video}")
    print(f"🖼️ Image: {test_image}")
    print(f"📤 Output: {output_path}")
    print("="*50)
    
    try:
        # Load the video
        video = combine_videos(primary_video)
        print("✅ Video loaded successfully")
        
        # Add image overlay with animation at 2 seconds for 4 seconds
        print("🎭 Adding animated image overlay...")
        print("   ⬆️ Image will slide up from bottom")
        print("   ⬇️ Image will slide down and exit")
        
        video_with_image = add_image_overlay(
            video=video, 
            image_path=test_image, 
            start_time=2.0,  # Start at 2 seconds
            duration=4.0     # Show for 4 seconds
        )
        print("✅ Image overlay added with slide animation")
        
        # Write the final video
        print("🎥 Rendering final video...")
        video_with_image.write_videofile(
            output_path, 
            codec="h264", 
            audio_codec="aac", 
            threads=4, 
            bitrate="3000k"
        )
        
        # Clean up
        video.close()
        video_with_image.close()
        
        print("="*50)
        print("🎉 SUCCESS! Image animation test completed!")
        print(f"📁 Check the output: {output_path}")
        print("="*50)
        print("🎭 Animation Features:")
        print("   • Image slides UP from bottom (entrance)")
        print("   • Image stays centered for main duration")
        print("   • Image slides DOWN to bottom (exit)")
        print("   • Smooth easing animations")
        print("   • Fade in/out effects")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_image_animation()
