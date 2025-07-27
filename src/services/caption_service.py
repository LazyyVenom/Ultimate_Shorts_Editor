"""
Caption Service
Handles caption generation, processing, and integration
"""

import os
from typing import Optional, List, Dict, Any, Union
from moviepy import VideoFileClip, CompositeVideoClip

from ..models.project import Project
from ..models.media_file import MediaType


class CaptionService:
    """Service for handling captions and subtitles"""
    
    def __init__(self):
        """Initialize caption service"""
        self.integrator = None
        self.advanced_available = False
        
        # Try to import advanced caption integration
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from caption_integration import VideoCaptionIntegrator
            self.integrator = VideoCaptionIntegrator(model_size="base")
            self.advanced_available = True
            print("✅ Advanced caption service initialized")
        except ImportError as e:
            print(f"⚠️  Advanced caption features unavailable: {e}")
            print("Using basic caption functionality")
    
    def add_captions_from_audio(self, video: Union[VideoFileClip, CompositeVideoClip],
                               audio_path: str, font_path: Optional[str] = None,
                               word_by_word: bool = True, font_size: int = 32,
                               font_color: str = 'white') -> CompositeVideoClip:
        """Add auto-generated captions from audio file
        
        Args:
            video: Video clip to add captions to
            audio_path: Path to audio file for caption generation
            font_path: Path to font file (optional)
            word_by_word: Whether to show captions one word at a time
            font_size: Font size for captions
            font_color: Font color
            
        Returns:
            Video with captions added
        """
        if not os.path.exists(audio_path):
            print(f"❌ Audio file not found: {audio_path}")
            return CompositeVideoClip([video])
        
        if self.advanced_available and self.integrator:
            try:
                print(f"🎤 Generating captions from audio ({'word-by-word' if word_by_word else 'full-text'})...")
                
                # Use default font if none provided
                if font_path is None:
                    font_path = "static/Utendo-Bold.ttf"
                
                result = self.integrator.add_captions_to_video(
                    video=video,
                    audio_path=audio_path,
                    font_path=font_path,
                    font_size=font_size,
                    font_color=font_color,
                    word_by_word=word_by_word
                )
                
                print("✅ Captions added successfully")
                return result
                
            except Exception as e:
                print(f"❌ Error generating captions: {e}")
                return CompositeVideoClip([video])
        else:
            print("📝 Advanced caption generation not available")
            return CompositeVideoClip([video])
    
    def add_captions_from_srt(self, video: Union[VideoFileClip, CompositeVideoClip],
                             srt_path: str, font_path: Optional[str] = None,
                             font_size: int = 32, font_color: str = 'white') -> CompositeVideoClip:
        """Add captions from SRT file
        
        Args:
            video: Video clip to add captions to
            srt_path: Path to SRT subtitle file
            font_path: Path to font file (optional)
            font_size: Font size for captions
            font_color: Font color
            
        Returns:
            Video with captions added
        """
        if not os.path.exists(srt_path):
            print(f"❌ SRT file not found: {srt_path}")
            return CompositeVideoClip([video])
        
        if self.advanced_available and self.integrator:
            try:
                print(f"📄 Adding captions from SRT: {srt_path}")
                
                result = self.integrator.add_captions_to_video(
                    video=video,
                    srt_path=srt_path,
                    font_path=font_path,
                    font_size=font_size,
                    font_color=font_color
                )
                
                print("✅ SRT captions added successfully")
                return result
                
            except Exception as e:
                print(f"❌ Error adding SRT captions: {e}")
                return self._add_basic_srt_captions(video, srt_path, font_path, font_size, font_color)
        else:
            return self._add_basic_srt_captions(video, srt_path, font_path, font_size, font_color)
    
    def add_manual_captions(self, video: Union[VideoFileClip, CompositeVideoClip],
                           captions: List[Dict[str, Any]], font_path: Optional[str] = None,
                           font_size: int = 32, font_color: str = 'white',
                           word_by_word: bool = False) -> CompositeVideoClip:
        """Add manual captions from a list
        
        Args:
            video: Video clip to add captions to
            captions: List of caption dictionaries with 'text', 'start', 'duration'
            font_path: Path to font file (optional)
            font_size: Font size
            font_color: Font color
            word_by_word: Whether to show one word at a time
            
        Returns:
            Video with captions added
        """
        if self.advanced_available and self.integrator:
            try:
                print(f"📝 Adding manual captions ({len(captions)} segments)")
                
                result = self.integrator.add_captions_to_video(
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
                print(f"❌ Error adding manual captions: {e}")
                return self._add_basic_manual_captions(video, captions, font_path, font_size, font_color, word_by_word)
        else:
            return self._add_basic_manual_captions(video, captions, font_path, font_size, font_color, word_by_word)
    
    def _add_basic_srt_captions(self, video: Union[VideoFileClip, CompositeVideoClip],
                               srt_path: str, font_path: Optional[str],
                               font_size: int, font_color: str) -> CompositeVideoClip:
        """Basic SRT caption implementation"""
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
                    
                    # Position at 70% down from top
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
    
    def _parse_srt_file(self, srt_path: str) -> List[Dict[str, Any]]:
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
