"""
Color Grading Processor
Handles color correction, grading, and visual enhancement operations
"""

import os
import numpy as np
from typing import Union, Optional, Dict, Any, Tuple
from moviepy import VideoFileClip, CompositeVideoClip, ColorClip
from moviepy import vfx
from dataclasses import dataclass


@dataclass
class ColorGradingSettings:
    """Settings for color grading operations"""
    
    # Basic adjustments
    brightness: float = 0.0  # -1.0 to 1.0
    contrast: float = 1.0    # 0.1 to 3.0
    saturation: float = 1.0  # 0.0 to 3.0
    gamma: float = 1.0       # 0.1 to 3.0
    
    # Color balance
    temperature: float = 0.0  # -1.0 (cooler) to 1.0 (warmer)
    tint: float = 0.0        # -1.0 (magenta) to 1.0 (green)
    
    # RGB adjustments
    red_gain: float = 1.0    # 0.0 to 2.0
    green_gain: float = 1.0  # 0.0 to 2.0
    blue_gain: float = 1.0   # 0.0 to 2.0
    
    # Advanced
    highlights: float = 0.0   # -1.0 to 1.0
    shadows: float = 0.0      # -1.0 to 1.0
    clarity: float = 0.0      # -1.0 to 1.0
    vibrance: float = 0.0     # -1.0 to 1.0
    
    # LUT (Look Up Table) path
    lut_path: Optional[str] = None
    lut_intensity: float = 1.0  # 0.0 to 1.0


class ColorGradingProcessor:
    """Handles color grading and visual enhancement operations"""
    
    def __init__(self):
        """Initialize the color grading processor"""
        self.preset_luts = self._load_preset_luts()
        
    def _load_preset_luts(self) -> Dict[str, str]:
        """Load available preset LUTs"""
        luts_dir = os.path.join("static", "luts")
        luts = {}
        
        if os.path.exists(luts_dir):
            for file in os.listdir(luts_dir):
                if file.lower().endswith(('.cube', '.3dl', '.lut')):
                    name = os.path.splitext(file)[0]
                    luts[name] = os.path.join(luts_dir, file)
                    
        return luts
    
    def apply_color_grading(self, video: Union[VideoFileClip, CompositeVideoClip], 
                           settings: ColorGradingSettings) -> CompositeVideoClip:
        """Apply color grading to video based on settings
        
        Args:
            video: Input video clip
            settings: Color grading settings to apply
            
        Returns:
            Color graded video clip
        """
        try:
            # Start with the original video
            graded_video = video
            
            # Apply basic adjustments
            if settings.brightness != 0.0:
                graded_video = self._adjust_brightness(graded_video, settings.brightness)
                
            if settings.contrast != 1.0:
                graded_video = self._adjust_contrast(graded_video, settings.contrast)
                
            if settings.saturation != 1.0:
                graded_video = self._adjust_saturation(graded_video, settings.saturation)
                
            if settings.gamma != 1.0:
                graded_video = self._adjust_gamma(graded_video, settings.gamma)
            
            # Apply color temperature and tint
            if settings.temperature != 0.0 or settings.tint != 0.0:
                graded_video = self._adjust_color_balance(graded_video, settings.temperature, settings.tint)
            
            # Apply RGB gains
            if settings.red_gain != 1.0 or settings.green_gain != 1.0 or settings.blue_gain != 1.0:
                graded_video = self._adjust_rgb_gains(graded_video, settings.red_gain, settings.green_gain, settings.blue_gain)
            
            # Apply highlights and shadows
            if settings.highlights != 0.0 or settings.shadows != 0.0:
                graded_video = self._adjust_highlights_shadows(graded_video, settings.highlights, settings.shadows)
            
            # Apply clarity (unsharp mask)
            if settings.clarity != 0.0:
                graded_video = self._adjust_clarity(graded_video, settings.clarity)
            
            # Apply vibrance
            if settings.vibrance != 0.0:
                graded_video = self._adjust_vibrance(graded_video, settings.vibrance)
            
            # Apply LUT if specified
            if settings.lut_path and os.path.exists(settings.lut_path):
                graded_video = self._apply_lut(graded_video, settings.lut_path, settings.lut_intensity)
            
            print("✅ Color grading applied successfully")
            return CompositeVideoClip([graded_video]) if not isinstance(graded_video, CompositeVideoClip) else graded_video
            
        except Exception as e:
            print(f"❌ Error applying color grading: {e}")
            return CompositeVideoClip([video])
    
    def _adjust_brightness(self, video: Union[VideoFileClip, CompositeVideoClip], brightness: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust video brightness"""
        def brightness_filter(get_frame, t):
            frame = get_frame(t)
            adjustment = brightness * 255
            frame = np.clip(frame.astype(np.float32) + adjustment, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(brightness_filter)
    
    def _adjust_contrast(self, video: Union[VideoFileClip, CompositeVideoClip], contrast: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust video contrast"""
        def contrast_filter(get_frame, t):
            frame = get_frame(t)
            frame = np.clip((frame.astype(np.float32) - 127.5) * contrast + 127.5, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(contrast_filter)
    
    def _adjust_saturation(self, video: Union[VideoFileClip, CompositeVideoClip], saturation: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust video saturation"""
        def saturation_filter(get_frame, t):
            frame = get_frame(t)
            # Convert to grayscale for luminance
            gray = np.dot(frame[...,:3], [0.299, 0.587, 0.114])
            gray = np.stack([gray, gray, gray], axis=-1)
            
            # Blend original with grayscale based on saturation
            frame = gray + saturation * (frame.astype(np.float32) - gray)
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(saturation_filter)
    
    def _adjust_gamma(self, video: Union[VideoFileClip, CompositeVideoClip], gamma: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust video gamma"""
        def gamma_filter(get_frame, t):
            frame = get_frame(t)
            frame = np.power(frame.astype(np.float32) / 255.0, 1.0 / gamma) * 255.0
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(gamma_filter)
    
    def _adjust_color_balance(self, video: Union[VideoFileClip, CompositeVideoClip], 
                             temperature: float, tint: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust color temperature and tint"""
        def color_balance_filter(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            
            # Temperature adjustment (blue/orange)
            if temperature > 0:  # Warmer
                frame[:, :, 0] *= (1 + temperature * 0.3)  # Red
                frame[:, :, 1] *= (1 + temperature * 0.1)  # Green
                frame[:, :, 2] *= (1 - temperature * 0.2)  # Blue
            elif temperature < 0:  # Cooler
                frame[:, :, 0] *= (1 + temperature * 0.2)  # Red
                frame[:, :, 1] *= (1 + temperature * 0.1)  # Green
                frame[:, :, 2] *= (1 - temperature * 0.3)  # Blue
            
            # Tint adjustment (green/magenta)
            if tint > 0:  # Green
                frame[:, :, 1] *= (1 + tint * 0.2)  # Green
                frame[:, :, 0] *= (1 - tint * 0.1)  # Red
                frame[:, :, 2] *= (1 - tint * 0.1)  # Blue
            elif tint < 0:  # Magenta
                frame[:, :, 0] *= (1 - tint * 0.1)  # Red
                frame[:, :, 1] *= (1 + tint * 0.2)  # Green
                frame[:, :, 2] *= (1 - tint * 0.1)  # Blue
            
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(color_balance_filter)
    
    def _adjust_rgb_gains(self, video: Union[VideoFileClip, CompositeVideoClip], 
                         red_gain: float, green_gain: float, blue_gain: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust individual RGB channel gains"""
        def rgb_gains_filter(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            frame[:, :, 0] *= red_gain    # Red
            frame[:, :, 1] *= green_gain  # Green
            frame[:, :, 2] *= blue_gain   # Blue
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(rgb_gains_filter)
    
    def _adjust_highlights_shadows(self, video: Union[VideoFileClip, CompositeVideoClip], 
                                  highlights: float, shadows: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust highlights and shadows"""
        def highlights_shadows_filter(get_frame, t):
            frame = get_frame(t).astype(np.float32) / 255.0
            
            # Create luminance mask
            luminance = np.dot(frame[...,:3], [0.299, 0.587, 0.114])
            
            # Highlights mask (bright areas)
            highlights_mask = np.power(luminance, 2)
            highlights_mask = np.stack([highlights_mask, highlights_mask, highlights_mask], axis=-1)
            
            # Shadows mask (dark areas)
            shadows_mask = np.power(1 - luminance, 2)
            shadows_mask = np.stack([shadows_mask, shadows_mask, shadows_mask], axis=-1)
            
            # Apply adjustments
            frame += highlights * highlights_mask * (0.5 - frame)
            frame += shadows * shadows_mask * (0.5 - frame)
            
            frame = np.clip(frame * 255.0, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(highlights_shadows_filter)
    
    def _adjust_clarity(self, video: Union[VideoFileClip, CompositeVideoClip], clarity: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust clarity using unsharp mask"""
        def clarity_filter(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            
            if clarity != 0:
                # Simple unsharp mask approximation
                # In a full implementation, you'd use proper gaussian blur
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * clarity * 0.1
                # This is a simplified version - proper implementation would use convolution
                
            return frame.astype(np.uint8)
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(clarity_filter)
    
    def _adjust_vibrance(self, video: Union[VideoFileClip, CompositeVideoClip], vibrance: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Adjust vibrance (smart saturation)"""
        def vibrance_filter(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            
            # Calculate saturation level for each pixel
            max_rgb = np.max(frame, axis=2)
            min_rgb = np.min(frame, axis=2)
            saturation_level = (max_rgb - min_rgb) / (max_rgb + 1e-8)
            
            # Apply vibrance more to less saturated areas
            vibrance_mask = 1 - saturation_level
            vibrance_mask = np.stack([vibrance_mask, vibrance_mask, vibrance_mask], axis=-1)
            
            # Apply saturation adjustment weighted by vibrance mask
            gray = np.dot(frame[...,:3], [0.299, 0.587, 0.114])
            gray = np.stack([gray, gray, gray], axis=-1)
            
            enhanced = gray + (1 + vibrance * vibrance_mask) * (frame - gray)
            frame = np.clip(enhanced, 0, 255).astype(np.uint8)
            return frame
        
        return video.with_fps(video.fps).with_duration(video.duration).transform(vibrance_filter)
    
    def _apply_lut(self, video: Union[VideoFileClip, CompositeVideoClip], 
                   lut_path: str, intensity: float) -> Union[VideoFileClip, CompositeVideoClip]:
        """Apply LUT (Look Up Table) to video"""
        try:
            # This is a simplified LUT application
            # In a full implementation, you'd parse .cube files properly
            print(f"📱 Applying LUT: {os.path.basename(lut_path)} (intensity: {intensity:.1f})")
            
            # For now, return the original video
            # TODO: Implement proper LUT parsing and application
            return video
            
        except Exception as e:
            print(f"Error applying LUT: {e}")
            return video
    
    def apply_preset(self, video: Union[VideoFileClip, CompositeVideoClip], 
                    preset_name: str) -> CompositeVideoClip:
        """Apply a predefined color grading preset
        
        Args:
            video: Input video
            preset_name: Name of the preset to apply
            
        Returns:
            Color graded video
        """
        presets = {
            "cinematic": ColorGradingSettings(
                contrast=1.2,
                saturation=0.9,
                temperature=-0.1,
                highlights=-0.2,
                shadows=0.1,
                vibrance=0.2
            ),
            "warm": ColorGradingSettings(
                temperature=0.3,
                brightness=0.05,
                contrast=1.1,
                saturation=1.1,
                vibrance=0.1
            ),
            "cool": ColorGradingSettings(
                temperature=-0.3,
                brightness=0.02,
                contrast=1.05,
                saturation=1.05,
                clarity=0.1
            ),
            "vintage": ColorGradingSettings(
                contrast=0.9,
                saturation=0.7,
                gamma=1.1,
                temperature=0.2,
                red_gain=1.1,
                blue_gain=0.9,
                highlights=-0.1,
                shadows=0.2
            ),
            "high_contrast": ColorGradingSettings(
                contrast=1.4,
                clarity=0.3,
                highlights=-0.3,
                shadows=-0.2,
                vibrance=0.2
            ),
            "soft": ColorGradingSettings(
                contrast=0.8,
                brightness=0.05,
                highlights=0.1,
                shadows=0.15,
                saturation=0.9,
                gamma=1.1
            ),
            "vivid": ColorGradingSettings(
                saturation=1.3,
                vibrance=0.4,
                contrast=1.2,
                clarity=0.2,
                highlights=-0.1
            )
        }
        
        if preset_name not in presets:
            print(f"❌ Unknown preset: {preset_name}")
            return CompositeVideoClip([video])
        
        settings = presets[preset_name]
        print(f"🎨 Applying {preset_name} color grading preset")
        
        return self.apply_color_grading(video, settings)
    
    def get_available_presets(self) -> list[str]:
        """Get list of available color grading presets"""
        return [
            "cinematic", "warm", "cool", "vintage", 
            "high_contrast", "soft", "vivid"
        ]
    
    def get_available_luts(self) -> Dict[str, str]:
        """Get available LUT files"""
        return self.preset_luts.copy()
