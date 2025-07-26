"""
Simple example of how to use the Hinglish Captioner
"""

from audio_opp.captioner import HinglishCaptioner
import os

# Initialize the captioner
captioner = HinglishCaptioner(model_size="medium")

# Example 1: Caption an audio file
audio_file = "testing_stuff/overlay_audio.wav"
if os.path.exists(audio_file):
    print("Generating captions for audio file...")
    captions, output_files = captioner.generate_captions_from_audio(
        audio_file,
        output_dir="testing_stuff",
        save_formats=["srt", "json"]
    )
    
    print(f"Generated {len(captions)} caption segments")
    for format_type, file_path in output_files.items():
        print(f"{format_type.upper()} file: {file_path}")

# Example 2: Caption a video file (extracts audio automatically)
video_file = "testing_stuff/final_test_with_animations.mp4"
if os.path.exists(video_file):
    print("\nGenerating captions for video file...")
    captions, output_files = captioner.generate_captions_from_video(
        video_file,
        save_formats=["srt"]
    )
    
    print(f"Generated {len(captions)} caption segments from video")

# Example 3: Custom transcription settings for better Hinglish
audio_file = "testing_stuff/overlay_audio.wav"
if os.path.exists(audio_file):
    print("\nCustom transcription with specific settings...")
    
    # Direct transcription with custom parameters
    captions = captioner.transcribe_audio(
        audio_file,
        language="hi",  # Hindi for Hinglish
        vad_filter=True,  # Voice activity detection
        vad_parameters={
            "threshold": 0.5,
            "min_speech_duration_ms": 250,
            "max_speech_duration_s": 30,
            "min_silence_duration_ms": 100,
            "speech_pad_ms": 400
        }
    )
    
    # Format for video display
    formatted_captions = captioner.format_captions_for_video(
        captions,
        max_chars_per_line=35,  # Shorter lines for mobile
        max_lines=2
    )
    
    # Save as SRT for video editing
    captioner.save_captions(
        formatted_captions,
        "testing_stuff/custom_captions.srt",
        "srt"
    )
    
    print("Custom captions saved to testing_stuff/custom_captions.srt")
