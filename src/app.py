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
        self.color_grading_service = ColorGradingProcessor()
        
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
    
    def load_project(self, file_path: str) -> Project:
        """Load project from file
        
        Args:
            file_path: Path to project file
            
        Returns:
            Loaded Project instance
        """
        return self.project_service.load_project(file_path)
    
    def save_project(self, file_path: Optional[str] = None) -> str:
        """Save current project
        
        Args:
            file_path: Optional path to save to
            
        Returns:
            Path where project was saved
        """
        return self.project_service.save_project(file_path)
    
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
                         scale: float = 1.0, opacity: float = 1.0, **kwargs) -> bool:
        """Add image overlay to current project
        
        Args:
            image_path: Path to image file
            start_time: Start time in seconds
            duration: Duration in seconds
            position: Position of the overlay
            scale: Scale factor for the image
            opacity: Opacity of the overlay (0.0 to 1.0)
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
                scale=scale,
                opacity=opacity,
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
                        background_color: Optional[str] = None, **kwargs) -> bool:
        """Add text overlay to current project
        
        Args:
            text: Text content
            start_time: Start time in seconds
            duration: Duration in seconds
            position: Position of the text
            font_size: Size of the font
            font_color: Color of the text
            background_color: Background color (optional)
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
                font_size=font_size,
                font_color=font_color,
                background_color=background_color,
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
            
            # Create or load project
            if config_file and os.path.exists(config_file):
                self.load_project(config_file)
                print(f"✅ Loaded project from: {config_file}")
            else:
                self.create_project()
                print("✅ Created new project")
            
            # Create a VideoProject for the UI (simplified conversion for now)
            video_project = VideoProject()
            
            # Create and show main window
            main_window = MainWindow(video_project)
            main_window.show()
            
            print("🎬 Ultimate Shorts Editor started successfully!")
            print("📁 Use File > Open Project to load existing projects")
            print("📝 Use File > New Project to create new projects")
            
            # Start the application event loop
            if self.app:
                return self.app.exec_()
            return 1
            
        except ImportError as e:
            print(f"❌ GUI components not available: {e}")
            print("💡 Run in headless mode instead")
            return 1
    
    def run_headless(self, config_file: str, output_path: Optional[str] = None) -> int:
        """Run in headless mode for batch processing
        
        Args:
            config_file: Configuration file path
            output_path: Optional output path override
            
        Returns:
            Exit code
        """
        if not config_file or not os.path.exists(config_file):
            print("❌ Configuration file required for headless mode")
            return 1
        
        try:
            print("🎬 Running Ultimate Shorts Editor in headless mode...")
            
            # Load project
            project = self.load_project(config_file)
            
            # Override output path if provided
            if output_path:
                project.settings.output_directory = os.path.dirname(output_path)
                project.settings.output_filename = os.path.splitext(os.path.basename(output_path))[0]
            
            # Validate project
            issues = self.validate_project()
            if issues:
                print(f"❌ Project validation failed: {issues}")
                return 1
            
            # Export video
            output_file = self.export_video()
            
            if output_file:
                print(f"✅ Export completed: {output_file}")
                return 0
            else:
                print("❌ Export failed")
                return 1
                
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
        help='Project configuration file'
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
            # Headless mode
            if not args.config:
                print("❌ --config required for headless mode")
                return 1
            
            exit_code = app.run_headless(args.config, args.output)
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
