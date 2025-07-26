#!/usr/bin/env python3
"""
Test script for the Hinglish Captioner
Demonstrates usage with the overlay_audio.wav file
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from audio_opp.captioner import HinglishCaptioner

def test_audio_captioning():
    """Test the captioning functionality with overlay_audio.wav"""
    
    # Paths
    audio_file = "testing_stuff/overlay_audio.wav"
    output_dir = "testing_stuff/captions_output"
    
    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    print(f"🎵 Found audio file: {audio_file}")
    
    try:
        # Initialize the captioner with medium model for better accuracy
        print("🤖 Initializing Hinglish Captioner with medium model...")
        captioner = HinglishCaptioner(
            model_size="medium",  # Better for Hinglish
            device="auto",        # Auto-detect best device
            compute_type="auto"   # Auto-detect best compute type
        )
        
        # Generate captions
        print("🎬 Generating captions...")
        captions, output_paths = captioner.generate_captions_from_audio(
            audio_file,
            output_dir=output_dir,
            save_formats=["json", "srt", "vtt", "txt"]
        )
        
        # Display results
        print(f"\n✅ Successfully generated {len(captions)} caption segments!")
        print(f"📁 Output directory: {output_dir}")
        
        print("\n📄 Generated files:")
        for format_type, file_path in output_paths.items():
            print(f"  • {format_type.upper()}: {file_path}")
        
        # Show first few captions
        print(f"\n🔤 First {min(5, len(captions))} caption segments:")
        for i, caption in enumerate(captions[:5]):
            start_time = f"{caption['start']:.2f}s"
            end_time = f"{caption['end']:.2f}s"
            text = caption['text']
            print(f"  {i+1}. [{start_time} - {end_time}] {text}")
        
        # Show some statistics
        total_duration = captions[-1]['end'] if captions else 0
        avg_segment_length = sum(c['end'] - c['start'] for c in captions) / len(captions) if captions else 0
        
        print(f"\n📊 Statistics:")
        print(f"  • Total audio duration: {total_duration:.2f} seconds")
        print(f"  • Number of segments: {len(captions)}")
        print(f"  • Average segment length: {avg_segment_length:.2f} seconds")
        
        # Show formatted text example
        formatted_captions = captioner.format_captions_for_video(captions)
        if formatted_captions:
            print(f"\n📝 Formatted caption example:")
            example = formatted_captions[0]
            print(f"  Original: {example['text']}")
            print(f"  Formatted:\n    {example['formatted_text'].replace(chr(10), chr(10) + '    ')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during captioning: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_video_captioning():
    """Test captioning with video files"""
    
    # Look for video files in testing_stuff
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_files = []
    
    testing_dir = "testing_stuff"
    if os.path.exists(testing_dir):
        for file in os.listdir(testing_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(testing_dir, file))
    
    if not video_files:
        print("🎥 No video files found for testing video captioning")
        return
    
    # Use the first video file found
    video_file = video_files[0]
    print(f"\n🎥 Testing video captioning with: {video_file}")
    
    try:
        captioner = HinglishCaptioner(model_size="medium")
        captions, output_paths = captioner.generate_captions_from_video(
            video_file,
            output_dir="testing_stuff/video_captions_output",
            save_formats=["json", "srt"]
        )
        
        print(f"✅ Video captioning successful! Generated {len(captions)} segments")
        for format_type, path in output_paths.items():
            print(f"  • {format_type.upper()}: {path}")
            
    except Exception as e:
        print(f"❌ Video captioning failed: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Hinglish Captioner Tests")
    print("=" * 50)
    
    # Test audio captioning
    print("\n1️⃣ Testing Audio Captioning")
    print("-" * 30)
    success = test_audio_captioning()
    
    if success:
        # Test video captioning
        print("\n2️⃣ Testing Video Captioning")
        print("-" * 30)
        test_video_captioning()
    
    print("\n🏁 Tests completed!")

if __name__ == "__main__":
    main()
