"""
Export Service
Handles video export and rendering operations
"""

import os
from typing import Optional, Union, Callable, Dict, Any
from moviepy import VideoFileClip, CompositeVideoClip

from ..models.media_file import MediaFile, MediaType
from ..models.project import Project
from ..processors.video_processor import VideoProcessor
from ..processors.audio_processor import AudioProcessor
from ..processors.effect_processor import EffectProcessor
from .caption_service import CaptionService


class ExportService:
    """Service for handling video export and rendering"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize export service
        
        Args:
            temp_dir: Temporary directory for processing
        """
        self.temp_dir = temp_dir or os.path.join(os.getcwd(), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize processors
        self.video_processor = VideoProcessor()
        self.audio_processor = AudioProcessor()
        self.effect_processor = EffectProcessor()
        self.caption_service = CaptionService()
        
        # Progress tracking
        self.progress_callbacks: Dict[str, Callable] = {}
        self.current_video: Optional[Union[VideoFileClip, CompositeVideoClip]] = None
    
    def export_project(self, project: Project, 
                      progress_callback: Optional[Callable[[int, str], None]] = None) -> Optional[str]:
        """Export a complete project to video
        
        Args:
            project: Project to export
            progress_callback: Optional progress callback function
            
        Returns:
            Path to exported video or None if failed
        """
        if progress_callback:
            self.set_progress_callback('export', progress_callback)
        
        try:
            self.emit_progress('export', 5, "Starting export...")
            
            # Validate project
            issues = project.validate()
            if issues:
                print(f"❌ Project validation failed: {issues}")
                self.emit_progress('export', 0, f"Validation failed: {', '.join(issues)}")
                return None
            
            # Step 1: Load and combine primary video sources
            self.emit_progress('export', 15, "Loading video sources...")
            video = self._load_primary_video(project)
            if not video:
                self.emit_progress('export', 0, "Failed to load video sources")
                return None
            
            self.current_video = video
            
            # Step 2: Process audio
            self.emit_progress('export', 30, "Processing audio...")
            video = self._process_audio(project, video)
            
            # Step 3: Add overlays
            self.emit_progress('export', 50, "Adding overlays...")
            video = self._add_overlays(project, video)
            
            # Step 4: Add captions
            self.emit_progress('export', 70, "Adding captions...")
            video = self._add_captions(project, video)
            
            # Step 5: Apply effects
            self.emit_progress('export', 85, "Applying effects...")
            video = self._apply_effects(project, video)
            
            # Step 6: Export final video
            self.emit_progress('export', 90, "Exporting video...")
            output_path = self._export_final_video(project, video)
            
            if output_path:
                self.emit_progress('export', 100, "Export completed successfully!")
                print(f"✅ Video exported to: {output_path}")
                return output_path
            else:
                self.emit_progress('export', 0, "Export failed")
                return None
                
        except Exception as e:
            print(f"❌ Export error: {e}")
            self.emit_progress('export', 0, f"Export error: {str(e)}")
            return None
        finally:
            # Cleanup
            if self.current_video:
                try:
                    self.current_video.close()
                except:
                    pass
                self.current_video = None
    
    def create_preview(self, project: Project, duration: float = 10.0) -> Optional[str]:
        """Create a preview of the project
        
        Args:
            project: Project to preview
            duration: Duration of preview in seconds
            
        Returns:
            Path to preview video or None if failed
        """
        try:
            print(f"🎬 Creating {duration}s preview...")
            
            # Load primary video
            video = self._load_primary_video(project)
            if not video:
                return None
            
            # Limit duration
            preview_duration = min(duration, video.duration)
            preview = video.subclipped(0, preview_duration)
            
            # Quick processing (no heavy effects)
            preview = self._process_audio(project, preview, quick=True)
            preview = self._add_overlays(project, preview, quick=True)
            
            # Add preview watermark
            from moviepy import TextClip, CompositeVideoClip
            watermark = TextClip(
                text="PREVIEW",
                font_size=24,
                color='white',
                font='Arial-Bold'
            ).with_position(('right', 'top')).with_duration(preview_duration)
            
            preview = CompositeVideoClip([preview, watermark])
            
            # Export preview
            preview_path = os.path.join(self.temp_dir, f"preview_{project.name}.mp4")
            preview.write_videofile(
                preview_path,
                codec='h264',
                audio_codec='aac',
                fps=24,  # Lower FPS for faster preview
                bitrate='1000k',  # Lower bitrate
                verbose=False,
                logger=None
            )
            
            print(f"✅ Preview created: {preview_path}")
            return preview_path
            
        except Exception as e:
            print(f"❌ Preview creation failed: {e}")
            return None
    
    def set_progress_callback(self, callback_name: str, callback: Callable[[int, str], None]):
        """Set progress callback function"""
        self.progress_callbacks[callback_name] = callback
    
    def emit_progress(self, callback_name: str, progress: int, message: str = ""):
        """Emit progress update"""
        if callback_name in self.progress_callbacks:
            self.progress_callbacks[callback_name](progress, message)
    
    def _load_primary_video(self, project: Project) -> Optional[Union[VideoFileClip, CompositeVideoClip]]:
        """Load primary video source"""
        video_files = project.get_media_files_by_type(MediaType.VIDEO)
        if not video_files:
            print("❌ No video files in project")
            return None
        
        try:
            # Get the first video file as primary
            primary_video = video_files[0]
            video_clip = VideoFileClip(primary_video.file_path)
            
            # Check for secondary video to combine
            if len(video_files) > 1:
                secondary_video = video_files[1]
                return self.video_processor.combine_videos(
                    primary_video.file_path,
                    secondary_video.file_path
                )
            
            return video_clip
            
        except Exception as e:
            print(f"❌ Error loading video: {e}")
            return None
    
    def _process_audio(self, project: Project, video: Union[VideoFileClip, CompositeVideoClip], 
                      quick: bool = False) -> Union[VideoFileClip, CompositeVideoClip]:
        """Process audio tracks"""
        try:
            audio_files = project.get_media_files_by_type(MediaType.AUDIO)
            
            overlay_audio = None
            background_audio = None
            
            # Find audio files
            for audio_file in audio_files:
                identifier = audio_file.identifier or ""
                if 'overlay' in identifier.lower():
                    overlay_audio = audio_file.file_path
                elif 'background' in identifier.lower():
                    background_audio = audio_file.file_path
            
            if overlay_audio or background_audio:
                video = self.audio_processor.add_audio(
                    video, overlay_audio, background_audio
                )
            
            if not quick:
                # Apply audio effects
                video = self.audio_processor.fade_audio(video, 1.0, 1.0)
                video = self.audio_processor.normalize_audio(video)
            
            return video
            
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            return video
    
    def _add_overlays(self, project: Project, video: Union[VideoFileClip, CompositeVideoClip],
                     quick: bool = False) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add image and text overlays"""
        try:
            # Get overlay items from timeline
            overlay_items = [
                item for item in project.timeline.items
                if item.overlay and item.enabled
            ]
            
            for item in overlay_items:
                if item.overlay and hasattr(item.overlay, 'image_path'):
                    # Image overlay
                    video = self.effect_processor.add_image_overlay(
                        video,
                        item.overlay.image_path,
                        item.start_time,
                        item.duration
                    )
                elif item.overlay and hasattr(item.overlay, 'text'):
                    # Text overlay - import TextOverlay for type checking
                    from ..models.overlay import TextOverlay
                    if isinstance(item.overlay, TextOverlay):
                        video = self.effect_processor.add_text_overlay(
                            video,
                            item.overlay.text,
                            item.start_time,
                            item.duration,
                            item.overlay.font_path,
                            item.overlay.font_size,
                            item.overlay.font_color
                        )
            
            return video
            
        except Exception as e:
            print(f"❌ Error adding overlays: {e}")
            return video
    
    def _add_captions(self, project: Project, video: Union[VideoFileClip, CompositeVideoClip]) -> Union[VideoFileClip, CompositeVideoClip]:
        """Add captions to video"""
        if not project.settings.auto_captions:
            return video
        
        try:
            # Find audio file for caption generation
            audio_files = project.get_media_files_by_type(MediaType.AUDIO)
            overlay_audio = None
            
            for audio_file in audio_files:
                identifier = audio_file.identifier or ""
                if 'overlay' in identifier.lower():
                    overlay_audio = audio_file.file_path
                    break
            
            if overlay_audio:
                video = self.caption_service.add_captions_from_audio(
                    video,
                    overlay_audio,
                    font_path=project.settings.caption_font_path,
                    word_by_word=project.settings.word_by_word_captions,
                    font_size=project.settings.caption_font_size,
                    font_color=project.settings.caption_font_color
                )
            
            return video
            
        except Exception as e:
            print(f"❌ Error adding captions: {e}")
            return video
    
    def _apply_effects(self, project: Project, video: Union[VideoFileClip, CompositeVideoClip]) -> Union[VideoFileClip, CompositeVideoClip]:
        """Apply visual effects"""
        try:
            # Apply color grading
            if project.settings.color_grading != "none":
                video = self.effect_processor.apply_color_grading(
                    video, project.settings.color_grading
                )
            
            # Apply stabilization if enabled
            if project.settings.stabilization:
                # Basic stabilization implementation would go here
                pass
            
            return video
            
        except Exception as e:
            print(f"❌ Error applying effects: {e}")
            return video
    
    def _export_final_video(self, project: Project, video: Union[VideoFileClip, CompositeVideoClip]) -> Optional[str]:
        """Export final video file"""
        try:
            output_path = project.get_output_path()
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Export video
            video.write_videofile(
                output_path,
                codec=project.settings.output_codec,
                audio_codec=project.settings.audio_codec,
                bitrate=project.settings.output_bitrate,
                fps=project.settings.output_fps,
                threads=project.settings.threads,
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error exporting video: {e}")
            return None
