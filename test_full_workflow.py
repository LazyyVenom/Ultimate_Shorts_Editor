#!/usr/bin/env python3
"""
Test the application with the new slide animation using current settings
"""

import os
import sys
import tempfile
from vid_editor.utils import (
    add_image_overlay, add_text_overlay, combine_videos, add_audio
)

def test_full_workflow():
    """Test the complete workflow with slide animations"""
    
    print("🎬 ULTIMATE SHORTS EDITOR - ANIMATION TEST")
    print("="*60)
    
    # Test parameters (matching your recent configuration)
    primary_video = "testing_stuff/vid_1.mp4"
    secondary_video = "testing_stuff/vid_2.mp4"
    overlay_audio = "testing_stuff/overlay_audio.wav"
    image_overlays = [("testing_stuff/img_1.jpeg", "2.5")]
    text_overlays = [
        ("Gyaan Pellu", "5.5"),
        ("1.2", "7.0"),
        ("snidnsidsnis", "1.1")
    ]
    output_path = "testing_stuff/final_test_with_animations.mp4"
    
    print(f"📹 Primary Video: {primary_video}")
    print(f"📹 Secondary Video: {secondary_video}")
    print(f"🎵 Overlay Audio: {overlay_audio}")
    print(f"🖼️ Image Overlays: {len(image_overlays)} image")
    for idx, (img_path, timestamp) in enumerate(image_overlays):
        print(f"   📷 Image {idx+1}: {os.path.basename(img_path)} (at {timestamp}s) - WITH SLIDE ANIMATION")
    print(f"📝 Text Overlays: {len(text_overlays)} texts")
    for idx, (text_content, timestamp) in enumerate(text_overlays):
        print(f"   💬 Text {idx+1}: '{text_content}' (at {timestamp}s)")
    print("="*60)
    
    try:
        # Combine videos
        print("🎬 Combining videos...")
        video = combine_videos(primary_video, secondary_video)
        print("✅ Videos combined")
        
        # Add audio
        print("🎵 Adding audio tracks...")
        video = add_audio(video, overlay_audio, None)
        print("✅ Audio added")
        
        # Process image overlays with NEW SLIDE ANIMATION
        print("🎭 Adding animated image overlays...")
        for image_path, timestamp_str in image_overlays:
            if image_path and os.path.exists(image_path):
                # Parse timestamp
                try:
                    timestamp = float(timestamp_str.replace('s', ''))
                except:
                    timestamp = 0.0
                
                print(f"   🎪 Adding {os.path.basename(image_path)} with slide animation at {timestamp}s")
                video = add_image_overlay(video, image_path, timestamp, duration=4.0)
        print("✅ Animated image overlays added")
        
        # Process text overlays
        print("📝 Adding text overlays...")
        for text_content, timestamp_str in text_overlays:
            if text_content:
                # Parse timestamp
                try:
                    timestamp = float(timestamp_str.replace('s', ''))
                except:
                    timestamp = 0.0
                
                video = add_text_overlay(video, text_content, timestamp)
        print("✅ Text overlays added")
        
        # Write final video
        print("🎥 Rendering final video...")
        video.write_videofile(output_path, codec="h264", audio_codec="aac", threads=4, bitrate="3000k")
        video.close()
        
        print("="*60)
        print("🎉 SUCCESS! Complete workflow with slide animations!")
        print(f"📁 Final video: {output_path}")
        print("🎭 Features included:")
        print("   ✅ Video combination")
        print("   ✅ Audio overlay")
        print("   ✅ Animated image overlays (slide up/down)")
        print("   ✅ Text overlays")
        print("   ✅ Smooth animations and transitions")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_full_workflow()
