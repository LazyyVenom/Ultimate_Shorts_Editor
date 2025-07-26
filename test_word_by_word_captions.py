#!/usr/bin/env python3
"""
Test script for word-by-word caption functionality
"""

import os
from moviepy import VideoFileClip
from caption_integration import VideoCaptionIntegrator

def test_word_by_word_captions():
    """Test the word-by-word caption feature"""
    print("🔤 TESTING WORD-BY-WORD CAPTIONS")
    print("=" * 50)
    
    # Test files
    video_file = "testing_stuff/test_text_only.mp4"
    
    if not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return
    
    print(f"📹 Using video: {video_file}")
    
    try:
        # Load video
        video = VideoFileClip(video_file)
        print(f"   Duration: {video.duration:.1f}s")
        print(f"   Resolution: {video.size[0]}x{video.size[1]}")
        
        # Initialize integrator
        integrator = VideoCaptionIntegrator()
        
        # Test captions with different word counts
        test_captions = [
            {'text': 'Hello!', 'start': 1.0, 'duration': 1.0},  # Single word
            {'text': 'This is cool!', 'start': 2.5, 'duration': 2.0},  # Three words
            {'text': 'Word by word captions are awesome for engagement!', 'start': 5.0, 'duration': 4.0},  # Many words
            {'text': 'Perfect for social media content creation!', 'start': 9.5, 'duration': 3.5}  # Medium length
        ]
        
        print(f"\n📝 Testing {len(test_captions)} caption segments:")
        for i, caption in enumerate(test_captions, 1):
            words = caption['text'].split()
            word_duration = caption['duration'] / len(words)
            print(f"   {i}. '{caption['text']}' -> {len(words)} words @ {word_duration:.2f}s each")
        
        # Add word-by-word captions
        print("\n🔄 Generating word-by-word captions...")
        font_path = "static/Utendo-Bold.ttf" if os.path.exists("static/Utendo-Bold.ttf") else None
        
        result_video = integrator.add_captions_to_video(
            video=video,
            captions=test_captions,
            font_path=font_path,
            font_size=42,  # Larger for better visibility
            font_color='white',
            word_by_word=True
        )
        
        # Save result
        output_path = "testing_stuff/word_by_word_caption_test.mp4"
        print(f"\n💾 Saving to: {output_path}")
        result_video.write_videofile(output_path)
        
        print(f"\n✅ SUCCESS!")
        print(f"📁 Output: {output_path}")
        print("\n🎬 Features demonstrated:")
        print("   • Single word displays")
        print("   • Automatic timing distribution")
        print("   • Consistent positioning (30% from bottom)")
        print("   • Smooth word transitions")
        
        # Clean up
        video.close()
        result_video.close()
        
        # Also test comparison with full-text captions
        print("\n🔀 Creating comparison with full-text captions...")
        video2 = VideoFileClip(video_file)
        
        result_video2 = integrator.add_captions_to_video(
            video=video2,
            captions=test_captions,
            font_path=font_path,
            font_size=42,
            font_color='white',
            word_by_word=False  # Disable word-by-word for comparison
        )
        
        output_path2 = "testing_stuff/full_text_caption_comparison.mp4"
        result_video2.write_videofile(output_path2)
        
        print(f"📄 Full-text comparison saved: {output_path2}")
        
        # Clean up
        video2.close()
        result_video2.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_word_by_word_captions()
