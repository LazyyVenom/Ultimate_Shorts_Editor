#!/usr/bin/env python3
"""
Ultimate Shorts Editor - New Organized Structure
Main Application Entry Point
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Import new organized components
from src.core.video_project import VideoProject
from src.core.project_config import ProjectConfig
from src.ui.main_window import MainWindow


class UltimateShortEditor:
    """Main application class"""
    
    def __init__(self):
        """Initialize the Ultimate Shorts Editor application"""
        self.app = None
        self.main_window = None
        self.project = None
        
    def setup_application(self):
        """Setup PyQt5 application"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Ultimate Shorts Editor")
        self.app.setApplicationVersion("2.0")
        self.app.setOrganizationName("Video Editing Solutions")
        
        # Set application style
        self.app.setStyle('Fusion')
        
        # Enable high DPI scaling
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    def create_project(self, config_file: str = None) -> VideoProject:
        """Create or load a video project"""
        if config_file and os.path.exists(config_file):
            # Load existing project
            self.project = VideoProject.load_project(config_file)
            print(f"✅ Loaded project from: {config_file}")
        else:
            # Create new project
            config = ProjectConfig()
            self.project = VideoProject(config)
            print("✅ Created new project")
        
        return self.project
    
    def run(self, config_file: str = None, headless: bool = False):
        """Run the application
        
        Args:
            config_file: Optional project configuration file to load
            headless: Run without GUI for batch processing
        """
        if not headless:
            # GUI Mode
            self.setup_application()
            
            # Create project
            self.create_project(config_file)
            
            # Create and show main window
            self.main_window = MainWindow(self.project)
            self.main_window.show()
            
            print("🎬 Ultimate Shorts Editor started successfully!")
            print("📁 Use File > Open Project to load existing projects")
            print("📝 Use File > New Project to create new projects")
            
            # Start the application event loop
            return self.app.exec_()
        else:
            # Headless Mode (for batch processing)
            return self.run_headless(config_file)
    
    def run_headless(self, config_file: str) -> int:
        """Run in headless mode for batch processing"""
        if not config_file or not os.path.exists(config_file):
            print("❌ Configuration file required for headless mode")
            return 1
        
        try:
            print("🎬 Running Ultimate Shorts Editor in headless mode...")
            
            # Create project and load configuration
            self.create_project(config_file)
            
            # Set up progress callback
            def progress_callback(value, message=""):
                print(f"📊 Progress: {value}% - {message}")
            
            self.project.set_progress_callback('progress', progress_callback)
            
            # Process the video
            output_path = self.project.process_video()
            
            if output_path and os.path.exists(output_path):
                print(f"✅ Video processing completed successfully!")
                print(f"📁 Output saved to: {output_path}")
                return 0
            else:
                print("❌ Video processing failed")
                return 1
                
        except Exception as e:
            print(f"❌ Error in headless processing: {e}")
            return 1
        finally:
            if self.project:
                self.project.cleanup()


def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Ultimate Shorts Editor - Advanced Video Editing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start GUI mode
  python app_new.py
  
  # Load specific project in GUI
  python app_new.py --config project.json
  
  # Batch processing (headless mode)
  python app_new.py --config project.json --headless
  
  # Create sample configuration
  python app_new.py --create-sample-config
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to project configuration file'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode for batch processing'
    )
    
    parser.add_argument(
        '--create-sample-config',
        action='store_true',
        help='Create a sample configuration file'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='./output',
        help='Output directory for processed videos'
    )
    
    parser.add_argument(
        '--temp-dir', '-t',
        type=str,
        default='./temp',
        help='Temporary directory for processing'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.temp_dir, exist_ok=True)
    
    if args.create_sample_config:
        create_sample_config(args.output_dir)
        return 0
    
    # Create and run application
    editor = UltimateShortEditor()
    
    try:
        return editor.run(
            config_file=args.config,
            headless=args.headless
        )
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def create_sample_config(output_dir: str):
    """Create a sample configuration file"""
    config = ProjectConfig(
        project_name="Sample Project",
        output_directory=output_dir,
        primary_video="path/to/primary_video.mp4",
        secondary_video="path/to/secondary_video.mp4",
        overlay_audio="path/to/overlay_audio.mp3",
        background_audio="path/to/background_audio.mp3",
        auto_captions=True,
        word_by_word=True,
        image_overlays=[
            {
                "path": "path/to/image1.png",
                "timestamp": 5.0,
                "duration": 3.0
            }
        ],
        text_overlays=[
            {
                "text": "Sample Text Overlay",
                "timestamp": 10.0,
                "duration": 3.0,
                "animation": "fade"
            }
        ]
    )
    
    sample_path = os.path.join(output_dir, "sample_config.json")
    config.save_to_file(sample_path)
    
    print(f"✅ Sample configuration created: {sample_path}")
    print("📝 Edit this file with your actual media paths and settings")


if __name__ == "__main__":
    sys.exit(main())
