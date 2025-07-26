#!/usr/bin/env python3
"""
Test script for caption integration functionality
"""

import os
import sys

def test_caption_integration():
    """Test the caption integration components"""
    print("🧪 TESTING CAPTION INTEGRATION")
    print("=" * 40)
    
    # Test 1: Import caption integration
    print("\n1️⃣ Testing caption integration import...")
    try:
        from caption_integration import VideoCaptionIntegrator, SimpleCaptionIntegrator
        print("✅ Caption integration modules imported successfully")
        
        # Initialize integrators
        simple_integrator = SimpleCaptionIntegrator()
        video_integrator = VideoCaptionIntegrator()
        
        print(f"   📝 Simple integrator: {type(simple_integrator).__name__}")
        print(f"   🎤 Video integrator: {type(video_integrator).__name__}")
        print(f"   🔧 Advanced captioner available: {video_integrator.has_advanced_captioner}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Import from vid_editor.utils
    print("\n2️⃣ Testing utils integration...")
    try:
        from vid_editor.utils import add_captions_from_audio, CAPTIONS_AVAILABLE
        print("✅ Caption function imported from utils")
        print(f"   🔧 Captions available: {CAPTIONS_AVAILABLE}")
        
    except ImportError as e:
        print(f"❌ Utils import error: {e}")
        return False
    
    # Test 3: Test simple caption functionality
    print("\n3️⃣ Testing simple caption functionality...")
    try:
        # Test SRT parsing
        test_srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello World! This is a test caption.

2
00:00:05,000 --> 00:00:08,000
Second caption for testing.
"""
        
        # Write test SRT file
        test_srt_path = "testing_stuff/test_captions.srt"
        os.makedirs("testing_stuff", exist_ok=True)
        
        with open(test_srt_path, 'w', encoding='utf-8') as f:
            f.write(test_srt_content)
        
        # Parse SRT
        captions = simple_integrator._parse_srt_file(test_srt_path)
        print(f"✅ Parsed {len(captions)} captions from SRT")
        
        for i, caption in enumerate(captions):
            print(f"   📝 Caption {i+1}: '{caption['text']}' ({caption['start']:.1f}s - {caption['start'] + caption['duration']:.1f}s)")
        
        # Clean up
        if os.path.exists(test_srt_path):
            os.unlink(test_srt_path)
            
    except Exception as e:
        print(f"❌ Simple caption test error: {e}")
        return False
    
    # Test 4: Test with video (if available)
    test_video = "testing_stuff/test_text_only.mp4"
    if os.path.exists(test_video):
        print("\n4️⃣ Testing with real video...")
        try:
            from moviepy import VideoFileClip
            
            # Load video
            video = VideoFileClip(test_video)
            print(f"   📹 Video loaded: {video.duration:.1f}s, {video.size[0]}x{video.size[1]}")
            
            # Test simple captions
            test_captions = [
                {'text': 'Test Caption 1', 'start': 1.0, 'duration': 2.0},
                {'text': 'Test Caption 2', 'start': 4.0, 'duration': 2.0}
            ]
            
            result = simple_integrator.add_simple_captions(
                video, test_captions, font_size=32, font_color='white'
            )
            
            print(f"✅ Simple captions added to video")
            print(f"   🎬 Result type: {type(result).__name__}")
            print(f"   ⏱️  Duration: {result.duration:.1f}s")
            
            # Save test result
            output_path = "testing_stuff/test_caption_integration.mp4"
            result.write_videofile(output_path)
            print(f"✅ Test video with captions saved: {output_path}")
            
            # Clean up
            video.close()
            result.close()
            
        except Exception as e:
            print(f"❌ Video test error: {e}")
    else:
        print(f"\n4️⃣ Skipping video test - {test_video} not found")
    
    print("\n🎉 Caption integration test completed!")
    return True

if __name__ == "__main__":
    success = test_caption_integration()
    sys.exit(0 if success else 1)
