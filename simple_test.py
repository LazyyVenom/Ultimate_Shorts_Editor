#!/usr/bin/env python3
"""
Simple test for the captioner
"""

import os
from audio_opp.captioner import HinglishCaptioner

def main():
    print("🚀 Testing Hinglish Captioner")
    
    # Check if audio file exists
    audio_file = "testing_stuff/overlay_audio.wav"
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    print(f"✅ Found audio file: {audio_file}")
    
    try:
        # Initialize captioner
        print("🤖 Initializing captioner...")
        captioner = HinglishCaptioner(model_size="base")  # Use base model for faster testing
        
        # Generate captions
        print("🎬 Generating captions...")
        captions, output_paths = captioner.generate_captions_from_audio(
            audio_file,
            output_dir="testing_stuff",
            save_formats=["json", "srt"]
        )
        
        print(f"✅ Success! Generated {len(captions)} segments")
        
        # Show first caption
        if captions:
            first = captions[0]
            print(f"📝 First caption: [{first['start']:.2f}s-{first['end']:.2f}s] {first['text']}")
        
        print("📁 Output files:")
        for fmt, path in output_paths.items():
            print(f"  {fmt}: {path}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
