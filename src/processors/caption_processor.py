"""
Caption Processing Component
Handles caption generation, integration, and styling
"""

import os
from typing import Union, Optional, List, Dict, Any
from moviepy import VideoFileClip, CompositeVideoClip

# Import caption integration components
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from caption_integration import VideoCaptionIntegrator
    CAPTIONS_AVAILABLE = True
except ImportError:
    print("⚠️  Caption integration not available")
    CAPTIONS_AVAILABLE = False
    VideoCaptionIntegrator = None


class CaptionProcessor:
    """Handles caption processing operations"""
    
    def __init__(self, media_manager=None):
        global CAPTIONS_AVAILABLE
        self.media_manager = media_manager
        self.caption_integrator = None
        
        # Initialize caption integrator if available
        if CAPTIONS_AVAILABLE and VideoCaptionIntegrator:
            try:
                self.caption_integrator = VideoCaptionIntegrator(model_size="base")
                print("✅ Caption processor initialized with advanced features")
            except Exception as e:
                print(f"⚠️  Advanced caption features unavailable: {e}")
                CAPTIONS_AVAILABLE = False
    
    def add_captions_from_audio(self, video: Union[VideoFileClip, CompositeVideoClip], 
                               audio_path: str, font_path: Optional[str] = None, 
                               word_by_word: bool = True) -> CompositeVideoClip:
        """Add auto-generated captions from audio file to video
        
        Args:
            video: Video to add captions to
            audio_path: Path to audio file for caption generation
            font_path: Path to font file (optional)
            word_by_word: Whether to show captions one word at a time
            
        Returns:
            Video with captions added
        """
        if not CAPTIONS_AVAILABLE or not self.caption_integrator:
            print("📝 Caption integration not available - skipping captions")
            return CompositeVideoClip([video])
        
        if not os.path.exists(audio_path):
            print(f"Audio file not found for captions: {audio_path}")
            return CompositeVideoClip([video])
        
        try:
            caption_mode = "word-by-word" if word_by_word else "full-text"
            print(f"🎤 Generating captions from audio ({caption_mode})...")
            
            # Use the same font as text overlays
            if font_path is None:
                font_path = "static/Utendo-Bold.ttf"
            
            # Add captions to video with configurable word-by-word display
            result = self.caption_integrator.add_captions_to_video(
                video=video,
                audio_path=audio_path,
                font_path=font_path if os.path.exists(font_path) else None,
                font_size=32,  # Slightly smaller than manual text overlays
                font_color='white',
                word_by_word=word_by_word
            )
            
            print("✅ Captions added successfully")
            return result
            
        except Exception as e:
            print(f"Error adding captions from audio: {e}")
            return CompositeVideoClip([video])
    
    def add_captions_from_srt(self, video: Union[VideoFileClip, CompositeVideoClip], 
                             srt_path: str, font_path: Optional[str] = None, 
                             font_size: int = 32, font_color: str = 'white') -> CompositeVideoClip:
        """Add captions from SRT file to video
        
        Args:
            video: Video to add captions to
            srt_path: Path to SRT subtitle file
            font_path: Path to font file
            font_size: Font size for captions
            font_color: Font color
            
        Returns:
            Video with captions added
        """
        if not CAPTIONS_AVAILABLE or not self.caption_integrator:
            print("📝 Caption integration not available - using basic implementation")
            return self._add_basic_captions_from_srt(video, srt_path, font_path, font_size, font_color)
        
        try:
            result = self.caption_integrator.add_captions_to_video(
                video=video,
                srt_path=srt_path,
                font_path=font_path,
                font_size=font_size,
                font_color=font_color
            )
            
            print("✅ SRT captions added successfully")
            return result
            
        except Exception as e:
            print(f"Error adding SRT captions: {e}")
            return CompositeVideoClip([video])
    
    def add_manual_captions(self, video: Union[VideoFileClip, CompositeVideoClip], 
                           captions: List[Dict[str, Any]], font_path: Optional[str] = None, 
                           font_size: int = 32, font_color: str = 'white', 
                           word_by_word: bool = False) -> CompositeVideoClip:
        """Add manual captions to video
        
        Args:
            video: Video to add captions to
            captions: List of caption dictionaries with 'text', 'start', 'duration'
            font_path: Path to font file
            font_size: Font size
            font_color: Font color
            word_by_word: Whether to show one word at a time
            
        Returns:
            Video with captions added
        """
        if not CAPTIONS_AVAILABLE or not self.caption_integrator:
            print("📝 Caption integration not available - using basic implementation")
            return self._add_basic_manual_captions(video, captions, font_path, font_size, font_color, word_by_word)
        
        try:
            result = self.caption_integrator.add_captions_to_video(
                video=video,
                captions=captions,
                font_path=font_path,
                font_size=font_size,
                font_color=font_color,
                word_by_word=word_by_word
            )
            
            print("✅ Manual captions added successfully")
            return result
            
        except Exception as e:
            print(f"Error adding manual captions: {e}")
            return CompositeVideoClip([video])
    
    def _add_basic_captions_from_srt(self, video: Union[VideoFileClip, CompositeVideoClip], 
                                    srt_path: str, font_path: Optional[str], 
                                    font_size: int, font_color: str) -> CompositeVideoClip:
        """Basic SRT caption implementation without advanced features"""
        try:
            from moviepy import TextClip
            
            captions = self._parse_srt_file(srt_path)
            caption_clips = []
            
            for caption in captions:
                try:
                    txt_clip = TextClip(
                        text=caption['text'],
                        font_size=font_size,
                        color=font_color,
                        font=font_path,
                        method='caption',
                        size=(int(video.size[0] * 0.8), None)
                    )
                    
                    txt_clip = txt_clip.with_start(caption['start']).with_duration(caption['duration'])
                    
                    # Position at 70% down from top (30% from bottom)
                    vertical_pos = int(video.size[1] * 0.7)
                    txt_clip = txt_clip.with_position(('center', vertical_pos))
                    caption_clips.append(txt_clip)
                    
                except Exception as e:
                    print(f"Error creating caption clip: {e}")
                    continue
            
            if caption_clips:
                return CompositeVideoClip([video] + caption_clips)
            else:
                return CompositeVideoClip([video])
                
        except Exception as e:
            print(f"Error adding basic SRT captions: {e}")
            return CompositeVideoClip([video])
    
    def _add_basic_manual_captions(self, video: Union[VideoFileClip, CompositeVideoClip], 
                                  captions: List[Dict[str, Any]], font_path: Optional[str], 
                                  font_size: int, font_color: str, word_by_word: bool) -> CompositeVideoClip:
        """Basic manual caption implementation"""
        try:
            from moviepy import TextClip
            
            caption_clips = []
            
            for caption in captions:
                try:
                    text = str(caption['text'])
                    start_time = float(caption['start'])
                    duration = float(caption['duration'])
                    
                    if word_by_word:
                        # Split into individual words
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
                            
                            # Position at 70% down from top
                            vertical_pos = int(video.size[1] * 0.7)
                            txt_clip = txt_clip.with_position(('center', vertical_pos))
                            
                            caption_clips.append(txt_clip)
                    else:
                        # Full text caption
                        txt_clip = TextClip(
                            text=text,
                            font_size=font_size,
                            color=font_color,
                            font=font_path,
                            method='caption',
                            size=(int(video.size[0] * 0.8), None)
                        )
                        
                        txt_clip = txt_clip.with_start(start_time).with_duration(duration)
                        
                        # Position at 70% down from top
                        vertical_pos = int(video.size[1] * 0.7)
                        txt_clip = txt_clip.with_position(('center', vertical_pos))
                        
                        caption_clips.append(txt_clip)
                
                except Exception as e:
                    print(f"Error creating manual caption: {e}")
                    continue
            
            if caption_clips:
                return CompositeVideoClip([video] + caption_clips)
            else:
                return CompositeVideoClip([video])
                
        except Exception as e:
            print(f"Error adding basic manual captions: {e}")
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
