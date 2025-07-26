#!/usr/bin/env python3
"""
Test script for word-by-word caption generation from audio
Uses the HinglishCaptioner to generate captions with word-level timestamps
"""

import os
import sys
from moviepy import VideoFileClip, ColorClip
from caption_integration import VideoCaptionIntegrator

def test_audio_word_captions():
    """Test automatic word-by-word caption generation from audio"""
    
    print("🎤 Testing Automatic Word-by-Word Caption Generation from Audio")
    print("=" * 70)
    
    # Test files
    audio_file = "testing_stuff/overlay_audio.wav"
    
    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        print("Please ensure the audio file exists for testing")
        return
    
    try:
        # Initialize the caption integrator
        print("🔧 Initializing VideoCaptionIntegrator...")
        integrator = VideoCaptionIntegrator(model_size="medium")
        
        if not integrator.has_advanced_captioner:
            print("❌ Advanced captioner not available. Please install faster-whisper:")
            print("pip install faster-whisper")
            return
        
        # Create a simple test video (solid color background)
        print("🎬 Creating test video...")
        from moviepy import CompositeVideoClip
        test_video = CompositeVideoClip([ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=30)])  # 30-second black video
        
        # Test word-by-word caption generation
        print("📝 Generating word-by-word captions from audio...")
        result_video = integrator.add_captions_to_video(
            video=test_video,
            audio_path=audio_file,
            font_path="static/Utendo-Bold.ttf" if os.path.exists("static/Utendo-Bold.ttf") else None,
            font_size=40,
            font_color='white',
            word_by_word=True
        )
        
        # Save the result
        output_path = "testing_stuff/word_by_word_audio_captions_test.mp4"
        print(f"💾 Saving video with captions to: {output_path}")
        
        result_video.write_videofile(
            output_path,
            codec="h264",
            audio_codec="aac",
            fps=24,
            bitrate="2000k"
        )
        
        print("✅ Word-by-word caption test completed successfully!")
        print(f"📁 Output file: {output_path}")
        
        # Clean up
        test_video.close()
        result_video.close()
        
        # Also test the captioner directly for debugging
        print("\n🔍 Testing captioner directly for word-level analysis...")
        if integrator.captioner is not None:
            captions = integrator.captioner.transcribe_audio(
                audio_path=audio_file,
                language="hi",
                task="transcribe",
                vad_filter=True
            )
            
            print(f"📊 Analysis Results:")
            print(f"   Total segments: {len(captions)}")
            
            word_count = 0
            for i, segment in enumerate(captions[:3]):  # Show first 3 segments
                print(f"\n   Segment {i+1}: [{segment['start']:.2f}s - {segment['end']:.2f}s]")
                print(f"   Text: {segment['text']}")
                
                if 'words' in segment and segment['words']:
                    print(f"   Words ({len(segment['words'])}):")
                    for j, word_info in enumerate(segment['words'][:5]):  # Show first 5 words
                        print(f"     {j+1}. '{word_info['word']}' [{word_info['start']:.2f}s - {word_info['end']:.2f}s]")
                        word_count += 1
                    if len(segment['words']) > 5:
                        print(f"     ... and {len(segment['words']) - 5} more words")
                        word_count += len(segment['words']) - 5
                else:
                    print("   No word-level timestamps available")
            
            print(f"\n📈 Total words with timestamps: {word_count}")
        else:
            print("⚠️  Captioner not available for direct testing")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_word_captions()
