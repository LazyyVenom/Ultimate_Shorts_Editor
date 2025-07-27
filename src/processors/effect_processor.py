"""
Effect Processing Component
Handles visual effects, overlays, and color grading
"""

import os
from typing import Union, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip, CompositeVideoClip, TextClip, ImageClip, vfx
)


class EffectProcessor:
    """Handles visual effects and overlay processing"""
    
    def __init__(self, media_manager=None):
        self.media_manager = media_manager
    
    def add_image_overlay(self, video: Union[VideoFileClip, CompositeVideoClip], 
                         image_path: str, start_time: float, duration: float = 5.0) -> CompositeVideoClip:
        """Add an image overlay to the video at a specific timestamp
        
        Args:
            video: Base video clip
            image_path: Path to image file
            start_time: When to start showing the image (seconds)
            duration: How long to show the image (seconds)
            
        Returns:
            Video with image overlay
        """
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return CompositeVideoClip([video])
        
        try:
            img_clip = ImageClip(image_path)
            
            video_width, video_height = video.size
            img_width, img_height = img_clip.size
            
            # Scale image to fit 75% of video dimensions
            width_scale = (video_width * 0.75) / img_width
            height_scale = (video_height * 0.75) / img_height
            scale_factor = min(width_scale, height_scale)
            
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            
            img_clip = img_clip.resized((new_width, new_height))
            
            # Adjust duration if it extends beyond video end
            img_duration = min(duration, video.duration - start_time)
            if img_duration <= 0:
                print(f"Image at {start_time}s would appear after video ends.")
                return CompositeVideoClip([video])
            
            img_clip = img_clip.with_start(start_time).with_duration(img_duration)
            
            # Position the image in the center
            center_x = (video_width - new_width) // 2
            center_y = (video_height - new_height) // 2
            img_clip = img_clip.with_position((center_x, center_y))
            
            # Add fade effects for smooth entrance and exit
            fade_duration = min(0.5, img_duration / 4)
            img_clip = img_clip.with_effects([vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)])
            
            # Create slide animation if duration is long enough
            if img_duration > 1.0:
                img_clip = self._add_slide_animation(img_clip, center_x, center_y, video_height, img_duration)
            
            result = CompositeVideoClip([video, img_clip])
            return result
        
        except Exception as e:
            print(f"Error adding image overlay: {e}")
            return CompositeVideoClip([video])
    
    def _add_slide_animation(self, img_clip, center_x: int, center_y: int, 
                           video_height: int, img_duration: float):
        """Add slide-up entrance and slide-down exit animation"""
        animation_duration = min(0.6, img_duration / 3)
        
        def slide_position(t):
            if t < animation_duration:
                # Slide up from bottom
                progress = t / animation_duration
                # Ease-out effect
                progress = 1 - (1 - progress) ** 2
                # Start from below screen
                start_y = video_height
                current_y = start_y - (start_y - center_y) * progress
                return (center_x, max(0, min(video_height, int(current_y))))
            elif t > img_duration - animation_duration:
                # Slide down to bottom
                exit_progress = (t - (img_duration - animation_duration)) / animation_duration
                # Ease-in effect
                exit_progress = exit_progress ** 2
                # Move to below screen
                end_y = video_height
                current_y = center_y + (end_y - center_y) * exit_progress
                return (center_x, max(0, min(video_height, int(current_y))))
            else:
                # Stay in center
                return (center_x, center_y)
        
        # Apply the slide animation
        return img_clip.with_position(slide_position)
    
    def add_text_overlay(self, video: Union[VideoFileClip, CompositeVideoClip], 
                        text: str, start_time: float, duration: float = 3.0, 
                        animation: str = "fade") -> CompositeVideoClip:
        """Add animated text overlay to the video
        
        Args:
            video: Base video clip
            text: Text to display
            start_time: When to start displaying the text (seconds)
            duration: How long to display the text (seconds)
            animation: Animation type ("slide", "fade", "zoom", "typewriter")
            
        Returns:
            Video with text overlay
        """
        try:
            font_path = "static/Utendo-Bold.ttf"
            
            try:
                text_clip = TextClip(
                    text=text,
                    font=font_path,
                    font_size=40,
                    color='white',
                    bg_color=None,
                    method='caption',
                    size=(int(video.size[0] * 0.8), None),
                    text_align='center'
                )
            except Exception:
                text_clip = TextClip(
                    text=text,
                    font_size=40,
                    color='white',
                    bg_color=None,
                    method='caption',
                    size=(int(video.size[0] * 0.8), None),
                    text_align='center'
                )
            
            text_duration = min(duration, video.duration - start_time)
            if text_duration <= 0:
                print(f"Text at {start_time}s would appear after video ends.")
                return CompositeVideoClip([video]) if isinstance(video, VideoFileClip) else video
                
            # Position text at 70% from top (30% from bottom)
            vertical_position = int(video.size[1] * 0.7)
            text_clip = text_clip.with_position(('center', vertical_position)).with_start(start_time).with_duration(text_duration)
            
            # Apply animation
            text_clip = self._apply_text_animation(text_clip, animation, text_duration)
            
            result = CompositeVideoClip([video, text_clip])
            return result
        
        except Exception as e:
            print(f"Error adding text overlay: {e}")
            return CompositeVideoClip([video]) if isinstance(video, VideoFileClip) else video
    
    def _apply_text_animation(self, text_clip, animation: str, text_duration: float):
        """Apply animation effects to text clip"""
        anim_duration = min(0.7, text_duration / 4)
        
        if animation == "slide":
            return text_clip.with_effects([vfx.SlideIn(anim_duration, 'bottom'), vfx.SlideOut(anim_duration, 'bottom')])
            
        elif animation == "fade":
            return text_clip.with_effects([vfx.FadeIn(anim_duration), vfx.FadeOut(anim_duration)])
            
        elif animation == "zoom":
            try:
                # Create zoom effect using resize
                def zoom_effect(t):
                    if t < anim_duration:
                        # Zoom in
                        scale = 0.5 + 0.5 * (t / anim_duration)
                        return scale
                    elif t > text_duration - anim_duration:
                        # Zoom out
                        progress = (t - (text_duration - anim_duration)) / anim_duration
                        scale = 1.0 - 0.5 * progress
                        return scale
                    else:
                        return 1.0
                
                return text_clip.with_effects([vfx.Resize(lambda t: zoom_effect(t))])
            except:
                # Fallback to fade if zoom fails
                return text_clip.with_effects([vfx.FadeIn(anim_duration), vfx.FadeOut(anim_duration)])
            
        else:
            # Default: no animation
            return text_clip
    
    def apply_color_grading(self, video: Union[VideoFileClip, CompositeVideoClip], 
                           style: str = "cinematic") -> Union[VideoFileClip, CompositeVideoClip]:
        """Apply color grading effect to a video
        
        Args:
            video: Input video clip
            style: Color grading style ("cinematic", "warm", "cold", "vintage")
            
        Returns:
            Video with color grading applied
        """
        try:
            if style == "cinematic":
                return video.with_effects([vfx.MultiplyColor(factor=0.9)])
                
            elif style == "warm":
                def warm_filter(frame):
                    frame_float = frame.astype(np.float32)
                    frame_float[:,:,0] = np.minimum(frame_float[:,:,0] * 1.15, 255)  # Boost red
                    frame_float[:,:,1] = np.minimum(frame_float[:,:,1] * 1.05, 255)  # Slight green boost
                    frame_float[:,:,2] = np.maximum(frame_float[:,:,2] * 0.9, 0)     # Reduce blue
                    return frame_float.astype(np.uint8)
                    
                return video.with_effects([vfx.FX(warm_filter)])
                
            elif style == "cold":
                def cold_filter(frame):
                    frame_float = frame.astype(np.float32)
                    frame_float[:,:,0] = np.maximum(frame_float[:,:,0] * 0.9, 0)     # Reduce red
                    frame_float[:,:,2] = np.minimum(frame_float[:,:,2] * 1.15, 255)  # Boost blue
                    return frame_float.astype(np.uint8)
                    
                return video.with_effects([vfx.FX(cold_filter)])
                
            elif style == "vintage":
                def vintage_filter(frame):
                    frame_float = frame.astype(np.float32)
                    
                    # Apply sepia tone
                    r = frame_float[:,:,0] * 0.393 + frame_float[:,:,1] * 0.769 + frame_float[:,:,2] * 0.189
                    g = frame_float[:,:,0] * 0.349 + frame_float[:,:,1] * 0.686 + frame_float[:,:,2] * 0.168
                    b = frame_float[:,:,0] * 0.272 + frame_float[:,:,1] * 0.534 + frame_float[:,:,2] * 0.131
                    
                    frame_float[:,:,0] = np.minimum(r, 255)
                    frame_float[:,:,1] = np.minimum(g, 255)
                    frame_float[:,:,2] = np.minimum(b, 255)
                    
                    return np.clip(frame_float, 0, 255).astype(np.uint8)
                    
                return video.with_effects([vfx.FX(vintage_filter)])
                
            else:
                return video
                
        except Exception as e:
            print(f"Error applying color grading: {e}")
            return video
    
    def add_vignette(self, video: Union[VideoFileClip, CompositeVideoClip], 
                    intensity: float = 0.3) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add vignette effect to video
        
        Args:
            video: Input video clip
            intensity: Vignette intensity (0.0 to 1.0)
            
        Returns:
            Video with vignette effect
        """
        try:
            def vignette_filter(frame):
                rows, cols = frame.shape[:2]
                center_x, center_y = cols / 2, rows / 2
                
                # Create distance map from center
                y, x = np.ogrid[:rows, :cols]
                mask = ((x - center_x)**2 + (y - center_y)**2) / (max(center_x, center_y)**2)
                mask = np.minimum(mask, 1.0)
                
                # Apply vignette
                vignette_mask = 1.0 - mask * intensity
                
                frame_float = frame.astype(np.float32)
                for c in range(3):
                    frame_float[:,:,c] = frame_float[:,:,c] * vignette_mask
                
                return np.clip(frame_float, 0, 255).astype(np.uint8)
            
            return video.with_effects([vfx.FX(vignette_filter)])
            
        except Exception as e:
            print(f"Error adding vignette: {e}")
            return video
    
    def add_blur_effect(self, video: Union[VideoFileClip, CompositeVideoClip], 
                       blur_strength: float = 1.0) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add blur effect to video
        
        Args:
            video: Input video clip
            blur_strength: Blur strength (1.0 = normal, higher = more blur)
            
        Returns:
            Video with blur effect
        """
        try:
            # Simple blur implementation
            def blur_filter(frame):
                from scipy import ndimage
                return ndimage.gaussian_filter(frame, sigma=blur_strength)
            
            return video.with_effects([vfx.FX(blur_filter)])
            
        except ImportError:
            print("Warning: scipy not available for blur effect")
            return video
        except Exception as e:
            print(f"Error adding blur effect: {e}")
            return video
    
    def add_watermark(self, video: Union[VideoFileClip, CompositeVideoClip], 
                     watermark_text: str, position: str = "bottom-right", 
                     opacity: float = 0.7) -> CompositeVideoClip:
        """Add watermark text to video
        
        Args:
            video: Input video clip
            watermark_text: Text to use as watermark
            position: Position of watermark ("top-left", "top-right", "bottom-left", "bottom-right", "center")
            opacity: Watermark opacity (0.0 to 1.0)
            
        Returns:
            Video with watermark
        """
        try:
            watermark_clip = TextClip(
                text=watermark_text,
                font_size=24,
                color='white',
                method='label'
            ).with_duration(video.duration)
            
            # Set position
            if position == "top-left":
                watermark_clip = watermark_clip.with_position((20, 20))
            elif position == "top-right":
                watermark_clip = watermark_clip.with_position(('right', 'top'))
            elif position == "bottom-left":
                watermark_clip = watermark_clip.with_position((20, 'bottom'))
            elif position == "bottom-right":
                watermark_clip = watermark_clip.with_position(('right', 'bottom'))
            elif position == "center":
                watermark_clip = watermark_clip.with_position(('center', 'center'))
            else:
                watermark_clip = watermark_clip.with_position(('right', 'bottom'))
            
            # Set opacity
            watermark_clip = watermark_clip.with_opacity(opacity)
            
            return CompositeVideoClip([video, watermark_clip])
            
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return CompositeVideoClip([video])
