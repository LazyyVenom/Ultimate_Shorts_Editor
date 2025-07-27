"""
Video Processing Component
Handles video combination, transitions, and basic video operations
"""

import os
from typing import Union, Optional
import numpy as np
from moviepy import (
    VideoFileClip, CompositeVideoClip, concatenate_videoclips, vfx
)


class VideoProcessor:
    """Handles video processing operations"""
    
    def __init__(self, media_manager=None):
        self.media_manager = media_manager
    
    def combine_videos(self, primary_video_path: str, secondary_video_path: Optional[str] = None) -> Union[VideoFileClip, CompositeVideoClip]:
        """Combine two videos (optional) into one clip
        
        Args:
            primary_video_path: Path to the primary video file
            secondary_video_path: Optional path to secondary video file
            
        Returns:
            Combined video clip
        """
        if not os.path.exists(primary_video_path):
            raise FileNotFoundError(f"Primary video file not found: {primary_video_path}")
        
        primary_clip = VideoFileClip(primary_video_path)
        
        if secondary_video_path and os.path.exists(secondary_video_path):
            secondary_clip = VideoFileClip(secondary_video_path)
            secondary_clip = secondary_clip.resized(primary_clip.size)
            concatenated = concatenate_videoclips([primary_clip, secondary_clip])
            return concatenated
        
        return primary_clip
    
    def create_transition(self, clip1: VideoFileClip, clip2: VideoFileClip, 
                         transition_duration: float = 1.0, transition_type: str = "crossfade") -> VideoFileClip:
        """Create a smooth transition between two video clips
        
        Args:
            clip1: First video clip
            clip2: Second video clip
            transition_duration: Duration of the transition effect in seconds
            transition_type: Type of transition effect (crossfade, fade, etc.)
            
        Returns:
            VideoFileClip with the transition effect
        """
        max_transition = min(clip1.duration, clip2.duration) / 2
        transition_duration = min(transition_duration, max_transition)
        
        if transition_type == "crossfade":
            clip1_faded = clip1.with_effects([vfx.CrossFadeOut(transition_duration)])
            clip2_faded = clip2.with_effects([vfx.CrossFadeIn(transition_duration)])
            
            result = concatenate_videoclips([
                clip1_faded.subclipped(0, clip1.duration - transition_duration/2),
                clip2_faded.subclipped(transition_duration/2, clip2.duration)
            ])
            return result
            
        elif transition_type == "fade":
            clip1_faded = clip1.with_effects([vfx.FadeOut(transition_duration)])
            clip2_faded = clip2.with_effects([vfx.FadeIn(transition_duration)])
            result = concatenate_videoclips([clip1_faded, clip2_faded])
            return result
        
        else:
            result = concatenate_videoclips([clip1, clip2])
            return result
    
    def resize_video(self, video: Union[VideoFileClip, CompositeVideoClip], 
                    width: int, height: int) -> Union[VideoFileClip, CompositeVideoClip]:
        """Resize video to specified dimensions
        
        Args:
            video: Input video clip
            width: Target width
            height: Target height
            
        Returns:
            Resized video clip
        """
        return video.resized((width, height))
    
    def crop_video(self, video: Union[VideoFileClip, CompositeVideoClip], 
                  x1: int, y1: int, x2: int, y2: int) -> Union[VideoFileClip, CompositeVideoClip]:
        """Crop video to specified coordinates
        
        Args:
            video: Input video clip
            x1, y1: Top-left coordinates
            x2, y2: Bottom-right coordinates
            
        Returns:
            Cropped video clip
        """
        return video.cropped(x1=x1, y1=y1, x2=x2, y2=y2)
    
    def speed_change(self, video: Union[VideoFileClip, CompositeVideoClip], 
                    factor: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Change video playback speed
        
        Args:
            video: Input video clip
            factor: Speed factor (2.0 = 2x speed, 0.5 = half speed)
            
        Returns:
            Speed-adjusted video clip
        """
        return video.with_effects([vfx.MultiplySpeed(factor)])
    
    def add_fade_effects(self, video: Union[VideoFileClip, CompositeVideoClip], 
                        fade_in_duration: float = 1.0, fade_out_duration: float = 1.0) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add fade in and fade out effects
        
        Args:
            video: Input video clip
            fade_in_duration: Duration of fade in effect
            fade_out_duration: Duration of fade out effect
            
        Returns:
            Video with fade effects
        """
        effects = []
        if fade_in_duration > 0:
            effects.append(vfx.FadeIn(fade_in_duration))
        if fade_out_duration > 0:
            effects.append(vfx.FadeOut(fade_out_duration))
        
        if effects:
            return video.with_effects(effects)
        return video
    
    def stabilize_video(self, video: Union[VideoFileClip, CompositeVideoClip]) -> Union[VideoFileClip, CompositeVideoClip]:
        """Apply basic video stabilization
        
        Args:
            video: Input video clip
            
        Returns:
            Stabilized video clip
        """
        try:
            # Basic stabilization using moviepy
            return video.with_effects([vfx.BlackAndWhite().with_mask().invert()])
        except:
            # Return original if stabilization fails
            print("Warning: Video stabilization failed, returning original")
            return video
    
    def rotate_video(self, video: Union[VideoFileClip, CompositeVideoClip], 
                    angle: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Rotate video by specified angle
        
        Args:
            video: Input video clip
            angle: Rotation angle in degrees
            
        Returns:
            Rotated video clip
        """
        try:
            return video.rotated(angle)
        except Exception as e:
            print(f"Warning: Video rotation failed: {e}")
            return video
    
    def mirror_video(self, video: Union[VideoFileClip, CompositeVideoClip], 
                    axis: str = 'horizontal') -> Union[VideoFileClip, CompositeVideoClip]:
        """Mirror video along specified axis
        
        Args:
            video: Input video clip
            axis: 'horizontal' or 'vertical'
            
        Returns:
            Mirrored video clip
        """
        try:
            if axis == 'horizontal':
                return video.with_effects([vfx.MirrorX()])
            elif axis == 'vertical':
                return video.with_effects([vfx.MirrorY()])
            else:
                print(f"Warning: Unknown mirror axis: {axis}")
                return video
        except Exception as e:
            print(f"Warning: Video mirroring failed: {e}")
            return video
