"""
Advanced Hinglish Captioning Integration
Provides utilities for integrating captions with video editing workflow
"""

import os
import json
from typing import List, Dict, Tuple, Optional, Union
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

class SimpleCaptionIntegrator:
    """
    Simple caption integrator for basic subtitle functionality
    Compatible with MoviePy 2.x API
    """
    
    def __init__(self):
        """Initialize the simple caption integrator"""
        pass
    
    def add_captions_from_srt(
        self, 
        video: Union[VideoFileClip, CompositeVideoClip], 
        srt_path: str,
        font_path: Optional[str] = None,
        font_size: int = 40,
        font_color: str = 'white',
        position: str = 'bottom',
        margin: int = 50
    ) -> CompositeVideoClip:
        """
        Add captions from SRT file to video
        
        Args:
            video: Input video clip
            srt_path: Path to SRT subtitle file
            font_path: Path to custom font file
            font_size: Font size for captions
            font_color: Font color
            position: Caption position ('bottom', 'center', 'top')
            margin: Margin from edges
            
        Returns:
            CompositeVideoClip with captions
        """
        if not os.path.exists(srt_path):
            print(f"SRT file not found: {srt_path}")
            return CompositeVideoClip([video])
        
        # Parse SRT file
        captions = self._parse_srt_file(srt_path)
        
        # Create caption clips
        caption_clips = []
        
        for caption in captions:
            try:
                # Create text clip with updated API
                txt_clip = TextClip(
                    text=caption['text'],
                    font_size=font_size,
                    color=font_color,
                    font=font_path,
                    method='caption',
                    size=(int(video.size[0] * 0.8), None)  # 80% of video width
                )
                
                # Set timing using with_* methods
                txt_clip = txt_clip.with_start(caption['start']).with_duration(caption['duration'])
                
                # Position the text
                if position == 'bottom':
                    vertical_pos = int(video.size[1] * 0.85)  # 85% down from top
                elif position == 'top':
                    vertical_pos = int(video.size[1] * 0.15)  # 15% down from top
                else:  # center
                    vertical_pos = 'center'
                
                txt_clip = txt_clip.with_position(('center', vertical_pos))
                caption_clips.append(txt_clip)
                
            except Exception as e:
                print(f"Error creating caption clip: {e}")
                continue
        
        # Composite video with captions
        if caption_clips:
            return CompositeVideoClip([video] + caption_clips)
        else:
            return CompositeVideoClip([video])
    
    def add_simple_captions(
        self,
        video: Union[VideoFileClip, CompositeVideoClip],
        captions: List[Dict[str, Union[str, float]]],
        font_path: Optional[str] = None,
        font_size: int = 40,
        font_color: str = 'white',
        position: str = 'bottom',
        word_by_word: bool = True
    ) -> CompositeVideoClip:
        """
        Add simple captions from a list
        
        Args:
            video: Input video clip
            captions: List of caption dictionaries with 'text', 'start', 'duration'
            font_path: Path to custom font file
            font_size: Font size
            font_color: Font color
            position: Caption position
            word_by_word: If True, show one word at a time
            
        Returns:
            CompositeVideoClip with captions
        """
        caption_clips = []
        
        for caption in captions:
            try:
                # Ensure we have string text and numeric values
                text = str(caption['text'])
                start_time = float(caption['start'])
                duration = float(caption['duration'])
                
                if word_by_word:
                    # Split into individual words and create clips for each
                    words = text.split()
                    if not words:
                        continue
                        
                    word_duration = duration / len(words)
                    
                    for i, word in enumerate(words):
                        word_start = start_time + (i * word_duration)
                        
                        txt_clip = TextClip(
                            text=word,
                            font_size=font_size,
                            color=font_color,
                            font=font_path,
                            method='caption'
                        )
                        
                        txt_clip = txt_clip.with_start(word_start).with_duration(word_duration)
                        
                        # Position based on our text overlay logic (30% from bottom)
                        vertical_pos = int(video.size[1] * 0.7)
                        txt_clip = txt_clip.with_position(('center', vertical_pos))
                        
                        caption_clips.append(txt_clip)
                else:
                    # Original full-text caption behavior
                    txt_clip = TextClip(
                        text=text,
                        font_size=font_size,
                        color=font_color,
                        font=font_path,
                        method='caption',
                        size=(int(video.size[0] * 0.8), None)
                    )
                    
                    txt_clip = txt_clip.with_start(start_time).with_duration(duration)
                    
                    # Position based on our text overlay logic (30% from bottom)
                    vertical_pos = int(video.size[1] * 0.7)
                    txt_clip = txt_clip.with_position(('center', vertical_pos))
                    
                    caption_clips.append(txt_clip)
                
            except Exception as e:
                print(f"Error creating caption: {e}")
                continue
        
        if caption_clips:
            return CompositeVideoClip([video] + caption_clips)
        else:
            return CompositeVideoClip([video])
    
    def _parse_srt_file(self, srt_path: str) -> List[Dict]:
        """Parse SRT subtitle file"""
        captions = []
        
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            blocks = content.split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Parse timing
                    timing_line = lines[1]
                    if ' --> ' in timing_line:
                        start_str, end_str = timing_line.split(' --> ')
                        start_time = self._parse_srt_time(start_str)
                        end_time = self._parse_srt_time(end_str)
                        duration = end_time - start_time
                        
                        # Get text (may span multiple lines)
                        text = '\n'.join(lines[2:])
                        
                        captions.append({
                            'text': text,
                            'start': start_time,
                            'duration': duration
                        })
        
        except Exception as e:
            print(f"Error parsing SRT file: {e}")
        
        return captions
    
    def _parse_srt_time(self, time_str: str) -> float:
        """Parse SRT time format to seconds"""
        try:
            # Format: HH:MM:SS,mmm
            time_part, ms_part = time_str.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            
            return h * 3600 + m * 60 + s + ms / 1000.0
        except:
            return 0.0


class VideoCaptionIntegrator:
    """
    Enhanced caption integrator with fallback to simple captions
    """
    
    def __init__(self, model_size: str = "medium"):
        """Initialize the integrator with fallback"""
        self.simple_integrator = SimpleCaptionIntegrator()
        
        # Try to import advanced captioner
        try:
            from audio_opp.captioner import HinglishCaptioner
            self.captioner = HinglishCaptioner(model_size=model_size)
            self.has_advanced_captioner = True
            print(f"✅ Advanced Hinglish captioner loaded (model: {model_size})")
        except ImportError as e:
            print(f"⚠️  Advanced captioner not available: {e}")
            print("Using simple captions instead")
            self.captioner = None
            self.has_advanced_captioner = False
    
    def add_captions_to_video(
        self, 
        video: Union[VideoFileClip, CompositeVideoClip],
        audio_path: Optional[str] = None,
        srt_path: Optional[str] = None,
        captions: Optional[List[Dict]] = None,
        font_path: Optional[str] = None,
        font_size: int = 40,
        font_color: str = 'white',
        word_by_word: bool = True
    ) -> CompositeVideoClip:
        """
        Add captions to video with multiple input options
        
        Args:
            video: Input video clip
            audio_path: Path to audio file for auto-generation
            srt_path: Path to existing SRT file
            captions: Manual caption list
            font_path: Path to custom font
            font_size: Font size
            font_color: Font color
            word_by_word: If True, show one word at a time
            
        Returns:
            CompositeVideoClip with captions
        """
        # Priority: manual captions > SRT file > audio auto-generation
        if captions:
            print("📝 Using provided captions")
            return self.simple_integrator.add_simple_captions(
                video, captions, font_path, font_size, font_color, word_by_word=word_by_word
            )
        
        elif srt_path and os.path.exists(srt_path):
            print(f"📄 Using SRT file: {srt_path}")
            return self.simple_integrator.add_captions_from_srt(
                video, srt_path, font_path, font_size, font_color
            )
        
        elif audio_path and os.path.exists(audio_path) and self.has_advanced_captioner:
            print(f"🎤 Generating captions from audio: {audio_path}")
            return self._generate_captions_from_audio(
                video, audio_path, font_path, font_size, font_color, word_by_word
            )
        
        else:
            print("ℹ️  No caption source provided or available")
            return CompositeVideoClip([video])
    
    def _generate_captions_from_audio(
        self,
        video: Union[VideoFileClip, CompositeVideoClip],
        audio_path: str,
        font_path: Optional[str],
        font_size: int,
        font_color: str,
        word_by_word: bool = True
    ) -> CompositeVideoClip:
        """Generate captions from audio using advanced captioner with word-level timestamps"""
        if not self.has_advanced_captioner or self.captioner is None:
            print("❌ Advanced captioner not available")
            return CompositeVideoClip([video])
            
        try:
            print("🎤 Transcribing audio with word-level timestamps...")
            
            # Generate captions with word-level timestamps
            captions = self.captioner.transcribe_audio(
                audio_path=audio_path,
                language="hi",  # Hindi for Hinglish
                task="transcribe",
                vad_filter=True
            )
            
            print(f"📝 Generated {len(captions)} caption segments")
            
            # Convert to simple format for word-by-word display
            simple_captions = []
            
            if word_by_word:
                # Use word-level timestamps for individual word display
                for segment in captions:
                    if 'words' in segment and segment['words']:
                        # Use individual word timestamps
                        for word_info in segment['words']:
                            word_text = word_info['word'].strip()
                            if word_text:  # Skip empty words
                                simple_captions.append({
                                    'text': word_text,
                                    'start': word_info['start'],
                                    'duration': word_info['end'] - word_info['start']
                                })
                    else:
                        # Fallback: split segment text into words with even timing
                        segment_text = segment['text'].strip()
                        words = segment_text.split()
                        if words:
                            segment_duration = segment['end'] - segment['start']
                            word_duration = segment_duration / len(words)
                            
                            for i, word in enumerate(words):
                                word_start = segment['start'] + (i * word_duration)
                                simple_captions.append({
                                    'text': word,
                                    'start': word_start,
                                    'duration': word_duration
                                })
            else:
                # Full-text segments
                for segment in captions:
                    simple_captions.append({
                        'text': segment['text'],
                        'start': segment['start'],
                        'duration': segment['end'] - segment['start']
                    })
            
            print(f"🎬 Creating {len(simple_captions)} caption clips ({'word-by-word' if word_by_word else 'full-text'})")
            
            return self.simple_integrator.add_simple_captions(
                video, simple_captions, font_path, font_size, font_color, word_by_word=False  # Already split into words
            )
            
        except Exception as e:
            print(f"❌ Error generating captions from audio: {e}")
            import traceback
            traceback.print_exc()
            return CompositeVideoClip([video])


def demo_caption_integration():
    """
    Demonstration of caption integration features
    """
    print("🚀 Caption Integration Demo")
    print("=" * 40)
    
    # Initialize integrator
    integrator = VideoCaptionIntegrator(model_size="base")
    
    # Test files
    audio_file = "testing_stuff/overlay_audio.wav"
    video_file = "testing_stuff/test_text_only.mp4"
    
    # Test simple captions
    print("\n1️⃣ Testing simple captions...")
    
    if os.path.exists(video_file):
        try:
            # Load video
            from moviepy import VideoFileClip
            video = VideoFileClip(video_file)
            
            # Create sample captions for word-by-word testing
            sample_captions = [
                {'text': 'Welcome to our amazing video!', 'start': 1.0, 'duration': 3.0},
                {'text': 'This is a word by word caption test.', 'start': 4.0, 'duration': 4.0},
                {'text': 'Each word appears individually for better readability!', 'start': 8.0, 'duration': 5.0}
            ]
            
            # Add word-by-word captions
            font_path = "static/Utendo-Bold.ttf" if os.path.exists("static/Utendo-Bold.ttf") else None
            result_video = integrator.add_captions_to_video(
                video=video,
                captions=sample_captions,
                font_path=font_path,
                font_size=36,
                font_color='white',
                word_by_word=True  # Enable word-by-word display
            )
            
            # Save result
            output_path = "testing_stuff/video_with_word_by_word_captions.mp4"
            result_video.write_videofile(output_path)
            
            print(f"✅ Video with word-by-word captions saved: {output_path}")
            
            # Clean up
            video.close()
            result_video.close()
            
        except Exception as e:
            print(f"❌ Error in simple caption test: {e}")
    
    # Test audio caption generation (if available)
    if os.path.exists(audio_file) and integrator.has_advanced_captioner:
        print("\n2️⃣ Testing audio caption generation...")
        try:
            video = VideoFileClip(video_file)
            
            result_video = integrator.add_captions_to_video(
                video=video,
                audio_path=audio_file,
                font_path=font_path,
                font_size=36,
                font_color='white'
            )
            
            output_path = "testing_stuff/video_with_auto_captions.mp4"
            result_video.write_videofile(output_path)
            
            print(f"✅ Video with auto-generated captions saved: {output_path}")
            
            video.close()
            result_video.close()
            
        except Exception as e:
            print(f"❌ Error in auto caption test: {e}")
    
    print("\n🏁 Demo completed!")


if __name__ == "__main__":
    demo_caption_integration()
