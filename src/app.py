"""
Improved Main Application
Combines all the new organized components into a cohesive application
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication

# Import organized components
from .models.project import Project, ProjectSettings
from .models.media_file import MediaType
from .models.overlay import ImageOverlay, TextOverlay, Position
from .models.timeline import TimelineItem, TimelineItemType
from .services.media_service import MediaService
from .services.project_service import ProjectService
from .services.export_service import ExportService
from .services.caption_service import CaptionService
from .processors.color_grading_processor import ColorGradingProcessor, ColorGradingSettings


class UltimateShortEditorApplication:
    """
    Main application class that orchestrates all components
    Provides a clean, organized API for video editing operations
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize the application
        
        Args:
            temp_dir: Temporary directory for processing
        """
        # Setup directories
        self.temp_dir = temp_dir or os.path.join(os.getcwd(), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
                # Initialize services
        self.media_service = MediaService(self.temp_dir)
        self.project_service = ProjectService()
        self.export_service = ExportService(self.temp_dir)
        self.caption_service = CaptionService()
        
        # Initialize processors
        self.color_grading_processor = ColorGradingProcessor()
        
        # Application state
        self.app: Optional[QApplication] = None
        self.gui_mode = False
        
        print("🎬 Ultimate Shorts Editor initialized")
        print(f"📁 Working directory: {self.temp_dir}")
    
    def setup_gui(self) -> QApplication:
        """Setup PyQt5 application for GUI mode
        
        Returns:
            QApplication instance
        """
        if not self.app:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Ultimate Shorts Editor")
            self.app.setApplicationVersion("2.0")
            self.app.setOrganizationName("Video Editing Solutions")
            
            # Set application style
            self.app.setStyle('Fusion')
            
            # Basic Qt setup
            self.app.setApplicationName("Ultimate Shorts Editor")
            self.app.setApplicationVersion("2.0.0")
            
            self.gui_mode = True
            print("✅ GUI mode initialized")
        
        return self.app
    
    def create_project(self, name: str = "New Project", **settings) -> Project:
        """Create a new project
        
        Args:
            name: Project name
            **settings: Additional project settings
            
        Returns:
            New Project instance
        """
        return self.project_service.create_project(name, **settings)
    
    def add_media(self, file_path: str, identifier: Optional[str] = None) -> bool:
        """Add media file to current project
        
        Args:
            file_path: Path to media file
            identifier: Optional identifier
            
        Returns:
            True if added successfully
        """
        media_file = self.project_service.add_media_to_project(file_path, identifier)
        return media_file is not None
    
    def add_image_overlay(self, image_path: str, start_time: float, 
                         duration: float = 5.0, position: Position = Position.CENTER,
                         scale: float = 1.0, opacity: float = 1.0, rotation: float = 0.0,
                         fit_mode: str = "contain", custom_position: Optional[tuple] = None,
                         z_index: int = 1, **kwargs) -> bool:
        """Add image overlay to current project
        
        Args:
            image_path: Path to image file
            start_time: Start time in seconds
            duration: Duration in seconds
            position: Position of the overlay (CENTER, TOP, BOTTOM, etc.)
            scale: Scale factor for the image (1.0 = original size)
            opacity: Opacity of the overlay (0.0 to 1.0)
            rotation: Rotation angle in degrees
            fit_mode: How to fit the image ("contain", "cover", "fill", "stretch")
            custom_position: Custom position as (x, y) coordinates
            z_index: Layer order (higher values appear on top)
            **kwargs: Additional overlay properties
            
        Returns:
            True if added successfully
        """
        if not self.project_service.current_project:
            print("❌ No active project")
            return False
            
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False
            
        try:
            overlay = ImageOverlay(
                start_time=start_time,
                duration=duration,
                image_path=image_path,
                position=position,
                custom_position=custom_position,
                scale=scale,
                opacity=opacity,
                rotation=rotation,
                fit_mode=fit_mode,
                z_index=z_index,
                **kwargs
            )
            
            # Create timeline item for the overlay
            timeline_item = TimelineItem(
                item_type=TimelineItemType.IMAGE,
                start_time=start_time,
                duration=duration,
                track_index=2,  # Overlay track
                overlay=overlay
            )
            
            # Add to project timeline
            self.project_service.current_project.timeline.add_item(timeline_item)
            print(f"✅ Added image overlay: {os.path.basename(image_path)} at {start_time}s")
            return True
            
        except Exception as e:
            print(f"❌ Error adding image overlay: {e}")
            return False
    
    def add_text_overlay(self, text: str, start_time: float, 
                        duration: float = 3.0, position: Position = Position.BOTTOM,
                        font_size: int = 40, font_color: str = "white",
                        background_color: Optional[str] = None, 
                        font_path: Optional[str] = None,
                        stroke_color: Optional[str] = None, stroke_width: int = 0,
                        text_align: str = "center", line_spacing: float = 1.2,
                        max_width: Optional[int] = None, custom_position: Optional[tuple] = None,
                        z_index: int = 2, opacity: float = 1.0, **kwargs) -> bool:
        """Add text overlay to current project
        
        Args:
            text: Text content
            start_time: Start time in seconds
            duration: Duration in seconds
            position: Position of the text (CENTER, TOP, BOTTOM, etc.)
            font_size: Size of the font
            font_color: Color of the text (name or hex)
            background_color: Background color (optional)
            font_path: Path to custom font file (optional)
            stroke_color: Text stroke/outline color (optional)
            stroke_width: Width of text stroke in pixels
            text_align: Text alignment ("left", "center", "right")
            line_spacing: Line spacing multiplier
            max_width: Maximum width for text wrapping (pixels)
            custom_position: Custom position as (x, y) coordinates
            z_index: Layer order (higher values appear on top)
            opacity: Text opacity (0.0 to 1.0)
            **kwargs: Additional overlay properties
            
        Returns:
            True if added successfully
        """
        if not self.project_service.current_project:
            print("❌ No active project")
            return False
            
        try:
            overlay = TextOverlay(
                start_time=start_time,
                duration=duration,
                text=text,
                position=position,
                custom_position=custom_position,
                font_size=font_size,
                font_color=font_color,
                background_color=background_color,
                font_path=font_path,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                text_align=text_align,
                line_spacing=line_spacing,
                max_width=max_width,
                z_index=z_index,
                opacity=opacity,
                **kwargs
            )
            
            # Create timeline item for the overlay
            timeline_item = TimelineItem(
                item_type=TimelineItemType.TEXT,
                start_time=start_time,
                duration=duration,
                track_index=3,  # Text track
                overlay=overlay  # This will need to be fixed in timeline model
            )
            
            # Add to project timeline
            self.project_service.current_project.timeline.add_item(timeline_item)
            print(f"✅ Added text overlay: '{text[:30]}...' at {start_time}s")
            return True
            
        except Exception as e:
            print(f"❌ Error adding text overlay: {e}")
            return False
    
    def apply_color_grading(self, settings: Optional[ColorGradingSettings] = None, **kwargs) -> bool:
        """Apply color grading to the current project
        
        Args:
            settings: ColorGradingSettings object with all adjustments
            **kwargs: Individual color grading parameters (brightness, contrast, etc.)
            
        Returns:
            True if applied successfully
        """
        if not self.project_service.current_project:
            print("❌ No active project")
            return False
            
        try:
            # Create settings from kwargs if not provided
            if settings is None:
                settings = ColorGradingSettings(**kwargs)
            
            # Store color grading settings in project settings as preset name
            self.project_service.current_project.settings.color_grading = "custom"
            
            print(f"✅ Applied color grading: brightness={settings.brightness}, contrast={settings.contrast}")
            return True
            
        except Exception as e:
            print(f"❌ Error applying color grading: {e}")
            return False
    
    def apply_color_grading_preset(self, preset_name: str) -> bool:
        """Apply a color grading preset to the current project
        
        Args:
            preset_name: Name of the preset (cinematic, warm, cool, vintage, etc.)
            
        Returns:
            True if applied successfully
        """
        if not self.project_service.current_project:
            print("❌ No active project")
            return False
            
        try:
            available_presets = self.color_grading_processor.get_available_presets()
            if preset_name not in available_presets:
                print(f"❌ Unknown preset: {preset_name}")
                print(f"Available presets: {', '.join(available_presets)}")
                return False
            
            # Store the preset name in project settings
            self.project_service.current_project.settings.color_grading = preset_name
            
            print(f"✅ Applied color grading preset: {preset_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error applying color grading preset: {e}")
            return False
    
    def get_available_color_presets(self) -> list[str]:
        """Get list of available color grading presets
        
        Returns:
            List of preset names
        """
        return self.color_grading_processor.get_available_presets()
    
    def add_multiple_overlays(self, overlays: List[Dict[str, Any]]) -> bool:
        """Add multiple overlays at once
        
        Args:
            overlays: List of overlay dictionaries with type, parameters
            
        Returns:
            True if all overlays added successfully
        """
        if not self.project_service.current_project:
            print("❌ No active project")
            return False
            
        success_count = 0
        for overlay_config in overlays:
            overlay_type = overlay_config.get('type', '').lower()
            
            if overlay_type == 'image':
                if self.add_image_overlay(**{k: v for k, v in overlay_config.items() if k != 'type'}):
                    success_count += 1
            elif overlay_type == 'text':
                if self.add_text_overlay(**{k: v for k, v in overlay_config.items() if k != 'type'}):
                    success_count += 1
            else:
                print(f"⚠️ Unknown overlay type: {overlay_type}")
        
        print(f"✅ Added {success_count}/{len(overlays)} overlays successfully")
        return success_count == len(overlays)
    
    def remove_overlay(self, start_time: float, overlay_type: Optional[str] = None) -> bool:
        """Remove overlay(s) at specific time
        
        Args:
            start_time: Start time of overlay to remove
            overlay_type: Optional type filter ('image' or 'text')
            
        Returns:
            True if overlay(s) removed successfully
        """
        if not self.project_service.current_project:
            print("❌ No active project")
            return False
            
        try:
            timeline = self.project_service.current_project.timeline
            items_to_remove = []
            
            for item in timeline.items:
                if (item.start_time == start_time and 
                    item.overlay is not None):
                    
                    if overlay_type is None:
                        items_to_remove.append(item)
                    elif (overlay_type.lower() == 'image' and 
                          item.item_type == TimelineItemType.IMAGE):
                        items_to_remove.append(item)
                    elif (overlay_type.lower() == 'text' and 
                          item.item_type == TimelineItemType.TEXT):
                        items_to_remove.append(item)
            
            for item in items_to_remove:
                timeline.items.remove(item)
            
            print(f"✅ Removed {len(items_to_remove)} overlay(s) at {start_time}s")
            return len(items_to_remove) > 0
            
        except Exception as e:
            print(f"❌ Error removing overlay: {e}")
            return False
    
    def list_overlays(self) -> List[Dict[str, Any]]:
        """List all overlays in the current project
        
        Returns:
            List of overlay information dictionaries
        """
        if not self.project_service.current_project:
            return []
            
        overlays = []
        timeline = self.project_service.current_project.timeline
        
        for item in timeline.items:
            if item.overlay is not None:
                overlay_info = {
                    'type': item.item_type.value,
                    'start_time': item.start_time,
                    'duration': item.duration,
                    'track_index': item.track_index
                }
                
                # Add specific overlay properties based on type
                if item.item_type == TimelineItemType.IMAGE:
                    overlay_info['image_path'] = getattr(item.overlay, 'image_path', '')
                    overlay_info['scale'] = getattr(item.overlay, 'scale', 1.0)
                elif item.item_type == TimelineItemType.TEXT:
                    overlay_info['text'] = getattr(item.overlay, 'text', '')
                    overlay_info['font_size'] = getattr(item.overlay, 'font_size', 40)
                    overlay_info['font_color'] = getattr(item.overlay, 'font_color', 'white')
                
                overlays.append(overlay_info)
        
        return overlays
    
    def export_video(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> Optional[str]:
        """Export current project to video
        
        Args:
            progress_callback: Optional progress callback function
            
        Returns:
            Path to exported video or None if failed
        """
        if not self.project_service.current_project:
            print("❌ No project loaded")
            return None
        
        return self.export_service.export_project(
            self.project_service.current_project,
            progress_callback
        )
    
    def create_preview(self, duration: float = 10.0) -> Optional[str]:
        """Create a preview of current project
        
        Args:
            duration: Duration of preview in seconds
            
        Returns:
            Path to preview video or None if failed
        """
        if not self.project_service.current_project:
            print("❌ No project loaded")
            return None
        
        return self.export_service.create_preview(
            self.project_service.current_project, duration
        )
    
    def validate_project(self) -> list[str]:
        """Validate current project
        
        Returns:
            List of validation issues
        """
        return self.project_service.validate_project()
    
    def get_project_info(self) -> Optional[dict]:
        """Get comprehensive project information
        
        Returns:
            Project information dictionary or None
        """
        return self.project_service.get_project_info()
    
    def get_supported_formats(self) -> dict:
        """Get all supported file formats
        
        Returns:
            Dictionary with media types and their supported extensions
        """
        return self.media_service.get_supported_formats()
    
    def validate_media_file(self, file_path: str) -> bool:
        """Validate a media file
        
        Args:
            file_path: Path to media file
            
        Returns:
            True if file is valid
        """
        return self.media_service.validate_media_file(file_path)
    
    def set_progress_callback(self, callback_name: str, callback: Callable[[int, str], None]):
        """Set progress callback function
        
        Args:
            callback_name: Name of the callback
            callback: Callback function (progress, message)
        """
        self.project_service.set_progress_callback(callback_name, callback)
        self.export_service.set_progress_callback(callback_name, callback)
    
    def run_gui(self, config_file: Optional[str] = None) -> int:
        """Run the application in GUI mode
        
        Args:
            config_file: Optional project configuration file to load
            
        Returns:
            Exit code
        """
        self.setup_gui()
        
        # Import UI components
        try:
            from .ui.main_window import MainWindow
            from .core.video_project import VideoProject
            
            # Always create a new project - keep it simple
            self.create_project()
            print("✅ Created new project")
            
            # Create a VideoProject for the UI (simplified conversion for now)
            video_project = VideoProject()
            
            # Create and show main window
            main_window = MainWindow(video_project)
            main_window.show()
            
            print("🎬 Ultimate Shorts Editor started successfully!")
            print("🎥 Ready to edit videos - add media, overlays, and effects!")
            
            # Start the application event loop
            if self.app:
                return self.app.exec_()
            return 1
            
        except ImportError as e:
            print(f"❌ GUI components not available: {e}")
            print("💡 Run in headless mode instead")
            return 1
    
    def run_headless(self, output_path: Optional[str] = None) -> int:
        """Run in headless mode for batch processing
        
        Args:
            output_path: Optional output path override
            
        Returns:
            Exit code
        """
        try:
            print("🎬 Running Ultimate Shorts Editor in headless mode...")
            
            # Create a new project
            self.create_project()
            
            # Override output path if provided
            if output_path and self.project_service.current_project:
                if hasattr(self.project_service.current_project, 'settings'):
                    self.project_service.current_project.settings.output_directory = os.path.dirname(output_path)
                    self.project_service.current_project.settings.output_filename = os.path.splitext(os.path.basename(output_path))[0]
            
            # Note: In headless mode, users would need to add media and configure 
            # the project programmatically before calling export_video()
            print("✅ Project created - ready for programmatic configuration")
            print("💡 Add media files and configure settings before exporting")
            
            return 0
                
        except Exception as e:
            print(f"❌ Headless processing failed: {e}")
            return 1
    
    def cleanup(self):
        """Clean up resources"""
        self.media_service.cleanup_temp_files()
        print("🧹 Cleanup completed")


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Ultimate Shorts Editor - Advanced Video Editing Tool"
    )
    parser.add_argument(
        '--config', '-c',
        help='Project configuration file (GUI mode only - optional)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output video file path (headless mode only)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode without GUI'
    )
    parser.add_argument(
        '--temp-dir',
        help='Temporary directory for processing'
    )
    
    args = parser.parse_args()
    
    # Create application
    app = UltimateShortEditorApplication(args.temp_dir)
    
    try:
        if args.headless:
            # Headless mode - no config required
            exit_code = app.run_headless(args.output)
        else:
            # GUI mode
            exit_code = app.run_gui(args.config)
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        app.cleanup()


if __name__ == "__main__":
    sys.exit(main())
