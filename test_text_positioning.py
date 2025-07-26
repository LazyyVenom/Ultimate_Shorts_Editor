#!/usr/bin/env python3
"""
Test script to verify text overlays appear at 70% height without animations
"""

import os
from moviepy import VideoFileClip
from vid_editor.utils import add_text_overlay

def main():
    print("📝 TESTING TEXT POSITIONING AT 70% HEIGHT")
    print("=" * 50)
    
    # Test parameters
    input_video = "testing_stuff/vid_1.mp4"
    output_video = "testing_stuff/test_text_70_percent.mp4"
    
    print(f"📹 Video: {input_video}")
    print(f"📤 Output: {output_video}")
    print("=" * 50)
    
    # Load video
    video = VideoFileClip(input_video)
    print("✅ Video loaded successfully")
    print(f"📏 Video dimensions: {video.size[0]}x{video.size[1]}")
    print(f"⏱️  Video duration: {video.duration:.1f}s")
    
    # Calculate where 70% height would be
    video_height = video.size[1]
    text_position_from_top = int(video_height * 0.3)  # 30% from top = 70% height
    print(f"📍 Text will appear at {text_position_from_top}px from top (70% height)")
    
    # Add text overlays at different times
    print("\n📝 Adding text overlays:")
    
    # Text 1: Early in video
    print("   💬 'Positioned at 70% Height!' at 1.0s")
    video = add_text_overlay(video, "Positioned at 70% Height!", 1.0, 2.0)
    
    # Text 2: Middle of video
    print("   💬 'No Fade Animations!' at 4.0s")
    video = add_text_overlay(video, "No Fade Animations!", 4.0, 2.0)
    
    # Text 3: Later in video
    print("   💬 'Perfect Text Position!' at 7.0s")
    video = add_text_overlay(video, "Perfect Text Position!", 7.0, 2.0)
    
    print("✅ All text overlays added successfully")
    
    # Save the result
    print("\n🎥 Rendering final video...")
    video.write_videofile(output_video)
    
    print("=" * 50)
    print("🎉 SUCCESS! Text positioning test completed!")
    print(f"📁 Check the output: {output_video}")
    print("📝 Text should appear at 70% height without fade animations")
    print("=" * 50)

if __name__ == "__main__":
    main()
