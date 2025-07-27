"""
Video Project Management
Core class for managing video editing projects
"""

import os
import time
from typing import Dict, Any, Optional, List, Union
from .project_config import ProjectConfig
from .media_manager import MediaManager
from ..processors.video_processor import VideoProcessor
from ..processors.audio_processor import AudioProcessor
from ..processors.caption_processor import CaptionProcessor
from ..processors.effect_processor import EffectProcessor


class VideoProject:
    """Main project class that orchestrates video editing operations"""
    
    def __init__(self, config: Optional[ProjectConfig] = None, temp_dir: Optional[str] = None):
        """Initialize video project
        
        Args:
            config: Project configuration
            temp_dir: Temporary directory for processing
        """
        self.config = config or ProjectConfig()
        self.temp_dir = temp_dir or os.path.join(os.getcwd(), "temp")
        
        # Initialize managers and processors
        self.media_manager = MediaManager(self.temp_dir)
        self.video_processor = VideoProcessor(self.media_manager)
        self.audio_processor = AudioProcessor(self.media_manager)
        self.caption_processor = CaptionProcessor(self.media_manager)
        self.effect_processor = EffectProcessor(self.media_manager)
        
        # Project state
        self.is_loaded = False
        self.current_video = None
        self.processing_callbacks = {}
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def set_progress_callback(self, callback_name: str, callback_func):
        """Set callback function for progress updates"""
        self.processing_callbacks[callback_name] = callback_func
    
    def emit_progress(self, callback_name: str, value: int, message: str = ""):
        """Emit progress update"""
        if callback_name in self.processing_callbacks:
            self.processing_callbacks[callback_name](value, message)
    
    def load_media(self) -> bool:
        """Load and validate all media files specified in config"""
        try:
            self.emit_progress('progress', 5, "Loading media files...")
            
            # Validate primary video (required)
            if not self.config.primary_video:
                raise ValueError("Primary video is required")
            
            if not self.media_manager.validate_video_file(self.config.primary_video):
                raise ValueError(f"Invalid primary video: {self.config.primary_video}")
            
            # Add primary video to media manager
            primary_media = self.media_manager.add_media_file(
                self.config.primary_video, 'video', 'primary_video'
            )
            
            # Load secondary video if specified
            if self.config.secondary_video:
                if not self.media_manager.validate_video_file(self.config.secondary_video):
                    print(f"Warning: Invalid secondary video: {self.config.secondary_video}")
                else:
                    self.media_manager.add_media_file(
                        self.config.secondary_video, 'video', 'secondary_video'
                    )
            
            # Load audio files if specified
            if self.config.overlay_audio:
                if not self.media_manager.validate_audio_file(self.config.overlay_audio):
                    print(f"Warning: Invalid overlay audio: {self.config.overlay_audio}")
                else:
                    self.media_manager.add_media_file(
                        self.config.overlay_audio, 'audio', 'overlay_audio'
                    )
            
            if self.config.background_audio:
                if not self.media_manager.validate_audio_file(self.config.background_audio):
                    print(f"Warning: Invalid background audio: {self.config.background_audio}")
                else:
                    self.media_manager.add_media_file(
                        self.config.background_audio, 'audio', 'background_audio'
                    )
            
            # Load image overlay files
            for overlay in self.config.image_overlays:
                image_path = overlay.get('path', '')
                if image_path and self.media_manager.validate_image_file(image_path):
                    identifier = f"image_overlay_{len([k for k in self.media_manager.media_files.keys() if k.startswith('image_overlay')])}"
                    self.media_manager.add_media_file(image_path, 'image', identifier)
            
            self.is_loaded = True
            self.emit_progress('progress', 15, "Media files loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading media: {e}")
            self.emit_progress('error', 0, str(e))
            return False
    
    def create_preview(self, duration: float = 5) -> Optional[str]:
        """Create a preview of the project"""
        if not self.is_loaded:
            if not self.load_media():
                return None
        
        try:
            self.emit_progress('progress', 20, "Creating preview...")
            
            primary_video = self.media_manager.get_media_file('primary_video')
            if not primary_video:
                return None
            
            preview_path = self.media_manager.create_preview(primary_video.file_path, duration)
            
            if preview_path:
                self.emit_progress('progress', 30, "Preview created successfully")
            
            return preview_path
            
        except Exception as e:
            print(f"Error creating preview: {e}")
            self.emit_progress('error', 0, str(e))
            return None
    
    def process_video(self) -> Optional[str]:
        """Process the complete video according to configuration"""
        if not self.is_loaded:
            if not self.load_media():
                return None
        
        try:
            self.emit_progress('progress', 35, "Starting video processing...")
            
            # Step 1: Combine videos
            video = self._combine_videos()
            if not video:
                raise ValueError("Failed to load/combine videos")
            
            self.current_video = video
            self.emit_progress('progress', 50, "Videos combined")
            
            # Step 2: Add audio
            video = self._add_audio(video)
            self.emit_progress('progress', 60, "Audio added")
            
            # Step 3: Add image overlays
            video = self._add_image_overlays(video)
            self.emit_progress('progress', 70, "Image overlays added")
            
            # Step 4: Add text overlays
            video = self._add_text_overlays(video)
            self.emit_progress('progress', 75, "Text overlays added")
            
            # Step 5: Add captions
            video = self._add_captions(video)
            self.emit_progress('progress', 85, "Captions added")
            
            # Step 6: Apply effects
            video = self._apply_effects(video)
            self.emit_progress('progress', 90, "Effects applied")
            
            # Step 7: Export video
            output_path = self._export_video(video)
            self.emit_progress('progress', 100, "Video processing complete")
            
            return output_path
            
        except Exception as e:
            print(f"Error processing video: {e}")
            self.emit_progress('error', 0, str(e))
            return None
        finally:
            # Cleanup
            if hasattr(self, 'current_video') and self.current_video:
                try:
                    self.current_video.close()
                except:
                    pass
    
    def _combine_videos(self):
        """Combine primary and secondary videos"""
        primary_media = self.media_manager.get_media_file('primary_video')
        secondary_media = self.media_manager.get_media_file('secondary_video')
        
        return self.video_processor.combine_videos(
            primary_media.file_path,
            secondary_media.file_path if secondary_media else None
        )
    
    def _add_audio(self, video):
        """Add overlay and background audio"""
        overlay_media = self.media_manager.get_media_file('overlay_audio')
        bg_media = self.media_manager.get_media_file('background_audio')
        
        return self.audio_processor.add_audio(
            video,
            overlay_media.file_path if overlay_media else None,
            bg_media.file_path if bg_media else None
        )
    
    def _add_image_overlays(self, video):
        """Add image overlays to video"""
        for overlay in self.config.image_overlays:
            image_path = overlay.get('path', '')
            timestamp = float(overlay.get('timestamp', 0))
            duration = float(overlay.get('duration', 5.0))
            
            if image_path and os.path.exists(image_path):
                video = self.effect_processor.add_image_overlay(
                    video, image_path, timestamp, duration
                )
        
        return video
    
    def _add_text_overlays(self, video):
        """Add text overlays to video"""
        for overlay in self.config.text_overlays:
            text = overlay.get('text', '')
            timestamp = float(overlay.get('timestamp', 0))
            duration = float(overlay.get('duration', 3.0))
            animation = overlay.get('animation', 'fade')
            
            if text:
                video = self.effect_processor.add_text_overlay(
                    video, text, timestamp, duration, animation
                )
        
        return video
    
    def _add_captions(self, video):
        """Add captions to video"""
        if not self.config.auto_captions:
            return video
        
        overlay_media = self.media_manager.get_media_file('overlay_audio')
        if not overlay_media:
            print("Auto-captions enabled but no overlay audio available")
            return video
        
        return self.caption_processor.add_captions_from_audio(
            video,
            overlay_media.file_path,
            self.config.caption_font_path,
            self.config.word_by_word
        )
    
    def _apply_effects(self, video):
        """Apply visual effects and color grading"""
        if self.config.color_grading != "none":
            video = self.effect_processor.apply_color_grading(video, self.config.color_grading)
        
        return video
    
    def _export_video(self, video) -> str:
        """Export the final video"""
        output_path = self.config.get_output_path()
        
        video.write_videofile(
            output_path,
            codec=self.config.output_codec,
            audio_codec="aac",
            threads=4,
            bitrate=self.config.output_bitrate,
            fps=self.config.output_fps
        )
        
        # Generate thumbnail
        self.media_manager.generate_thumbnail(output_path)
        
        return output_path
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get comprehensive project information"""
        info = {
            'config': self.config.to_dict(),
            'is_loaded': self.is_loaded,
            'media_files': {}
        }
        
        for identifier, media_file in self.media_manager.media_files.items():
            info['media_files'][identifier] = {
                'path': media_file.file_path,
                'type': media_file.media_type,
                'metadata': media_file.metadata,
                'is_valid': media_file.is_valid()
            }
        
        return info
    
    def save_project(self, file_path: str) -> None:
        """Save project configuration to file"""
        self.config.save_to_file(file_path)
    
    @classmethod
    def load_project(cls, file_path: str, temp_dir: Optional[str] = None) -> 'VideoProject':
        """Load project from configuration file"""
        config = ProjectConfig.load_from_file(file_path)
        return cls(config, temp_dir)
    
    def cleanup(self) -> None:
        """Clean up project resources"""
        if self.current_video:
            try:
                self.current_video.close()
            except:
                pass
        
        self.media_manager.cleanup_temp_files()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
