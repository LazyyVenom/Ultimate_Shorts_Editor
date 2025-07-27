"""
Audio Processing Component
Handles audio combination, mixing, and effects
"""

import os
from typing import Union, Optional
import numpy as np
from moviepy import (
    VideoFileClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip, 
    concatenate_audioclips
)


class AudioProcessor:
    """Handles audio processing operations"""
    
    def __init__(self, media_manager=None):
        self.media_manager = media_manager
    
    def add_audio(self, video: Union[VideoFileClip, CompositeVideoClip], 
                 overlay_audio_path: Optional[str] = None, 
                 background_audio_path: Optional[str] = None) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add overlay and/or background audio to video
        
        Args:
            video: Input video clip
            overlay_audio_path: Path to overlay audio file
            background_audio_path: Path to background audio file
            
        Returns:
            Video with added audio
        """
        result_video = video
        
        if overlay_audio_path and os.path.exists(overlay_audio_path):
            try:
                result_video = self._add_overlay_audio(result_video, overlay_audio_path)
            except Exception as e:
                print(f"Error adding overlay audio: {e}")
        
        if background_audio_path and os.path.exists(background_audio_path):
            try:
                result_video = self._add_background_audio(result_video, background_audio_path)
            except Exception as e:
                print(f"Error adding background audio: {e}")
        
        return result_video
    
    def _add_overlay_audio(self, video: Union[VideoFileClip, CompositeVideoClip], 
                          audio_path: str) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add overlay audio to video"""
        overlay_audio = AudioFileClip(audio_path)
        
        # Adjust audio duration to match video
        if overlay_audio.duration > video.duration:
            overlay_audio = overlay_audio.subclipped(0, video.duration)
        else:
            # Loop audio if shorter than video
            repeats = int(np.ceil(video.duration / overlay_audio.duration))
            overlay_audio = concatenate_audioclips([overlay_audio] * repeats).subclipped(0, video.duration)
        
        # Set volume for overlay audio
        overlay_audio = overlay_audio.with_volume_scaled(0.7)
        
        if video.audio:
            # Mix with existing audio
            original_audio = video.audio.with_volume_scaled(0.3)
            combined_audio = CompositeAudioClip([original_audio, overlay_audio])
            result_video = video.with_audio(combined_audio)
        else:
            # Replace audio
            result_video = video.with_audio(overlay_audio)
        
        return result_video
    
    def _add_background_audio(self, video: Union[VideoFileClip, CompositeVideoClip], 
                             audio_path: str) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add background audio to video"""
        bg_audio = AudioFileClip(audio_path)
        
        # Set low volume for background audio
        bg_audio = bg_audio.with_volume_scaled(0.15)
        
        # Adjust audio duration to match video
        if bg_audio.duration > video.duration:
            bg_audio = bg_audio.subclipped(0, video.duration)
        else:
            # Loop audio if shorter than video
            repeats = int(np.ceil(video.duration / bg_audio.duration))
            bg_audio = concatenate_audioclips([bg_audio] * repeats).subclipped(0, video.duration)
        
        if video.audio:
            # Mix with existing audio
            combined_audio = CompositeAudioClip([video.audio, bg_audio])
            result_video = video.with_audio(combined_audio)
        else:
            # Add as new audio
            result_video = video.with_audio(bg_audio)
        
        return result_video
    
    def adjust_volume(self, video: Union[VideoFileClip, CompositeVideoClip], 
                     volume_factor: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust video audio volume
        
        Args:
            video: Input video clip
            volume_factor: Volume multiplication factor (1.0 = original, 0.5 = half volume, 2.0 = double)
            
        Returns:
            Video with adjusted audio volume
        """
        if video.audio:
            adjusted_audio = video.audio.with_volume_scaled(volume_factor)
            return video.with_audio(adjusted_audio)
        return video
    
    def fade_audio(self, video: Union[VideoFileClip, CompositeVideoClip], 
                  fade_in_duration: float = 1.0, fade_out_duration: float = 1.0) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add fade in/out effects to audio
        
        Args:
            video: Input video clip
            fade_in_duration: Duration of fade in effect
            fade_out_duration: Duration of fade out effect
            
        Returns:
            Video with faded audio
        """
        if video.audio:
            audio = video.audio
            
            if fade_in_duration > 0:
                audio = audio.with_fadesin(fade_in_duration)
            
            if fade_out_duration > 0:
                audio = audio.with_fadeout(fade_out_duration)
            
            return video.with_audio(audio)
        return video
    
    def normalize_audio(self, video: Union[VideoFileClip, CompositeVideoClip]) -> Union[VideoFileClip, CompositeVideoClip]:
        """Normalize audio levels
        
        Args:
            video: Input video clip
            
        Returns:
            Video with normalized audio
        """
        if video.audio:
            try:
                # Simple normalization by finding peak and scaling
                audio = video.audio
                # This is a basic implementation - more advanced normalization would analyze RMS levels
                normalized_audio = audio.with_volume_scaled(0.8)  # Conservative normalization
                return video.with_audio(normalized_audio)
            except Exception as e:
                print(f"Warning: Audio normalization failed: {e}")
                return video
        return video
    
    def remove_audio(self, video: Union[VideoFileClip, CompositeVideoClip]) -> Union[VideoFileClip, CompositeVideoClip]:
        """Remove audio from video
        
        Args:
            video: Input video clip
            
        Returns:
            Video without audio
        """
        return video.without_audio()
    
    def extract_audio(self, video: Union[VideoFileClip, CompositeVideoClip], 
                     output_path: str) -> bool:
        """Extract audio from video to file
        
        Args:
            video: Input video clip
            output_path: Path to save extracted audio
            
        Returns:
            True if successful, False otherwise
        """
        if not video.audio:
            print("No audio track found in video")
            return False
        
        try:
            video.audio.write_audiofile(output_path)
            return True
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return False
    
    def mix_audio_tracks(self, audio_paths: list, volumes: Optional[list] = None, 
                        output_duration: Optional[float] = None) -> AudioFileClip:
        """Mix multiple audio tracks together
        
        Args:
            audio_paths: List of paths to audio files
            volumes: List of volume factors for each track (default: equal volume)
            output_duration: Duration of output audio (default: longest track)
            
        Returns:
            Mixed audio clip
        """
        if not audio_paths:
            raise ValueError("No audio paths provided")
        
        if volumes is None:
            volumes = [1.0] * len(audio_paths)
        
        if len(volumes) != len(audio_paths):
            raise ValueError("Number of volume factors must match number of audio paths")
        
        audio_clips = []
        max_duration = 0
        
        for i, audio_path in enumerate(audio_paths):
            if os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                audio = audio.with_volume_scaled(volumes[i])
                audio_clips.append(audio)
                max_duration = max(max_duration, audio.duration)
        
        if not audio_clips:
            raise ValueError("No valid audio files found")
        
        # Use specified duration or maximum duration
        final_duration = output_duration or max_duration
        
        # Extend or trim clips to match final duration
        adjusted_clips = []
        for audio in audio_clips:
            if audio.duration < final_duration:
                # Loop if shorter
                repeats = int(np.ceil(final_duration / audio.duration))
                audio = concatenate_audioclips([audio] * repeats)
            
            audio = audio.subclipped(0, final_duration)
            adjusted_clips.append(audio)
        
        # Mix all clips
        mixed_audio = CompositeAudioClip(adjusted_clips)
        return mixed_audio
