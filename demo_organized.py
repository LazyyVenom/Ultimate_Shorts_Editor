#!/usr/bin/env python3
"""
Demo Script - New Organized Architecture
Demonstrates how to use the new component-based system
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import UltimateShortEditorApplication
from src.models.project import Project
from src.models.media_file import MediaType
from src.services.media_service import MediaService
from src.services.project_service import ProjectService
from src.services.export_service import ExportService


def demo_basic_usage():
    """Demonstrate basic usage of the new system"""
    print("🎬 Ultimate Shorts Editor - New Architecture Demo")
    print("=" * 50)
    
    # Create application instance
    app = UltimateShortEditorApplication()
    
    # Create a new project
    print("\\n📝 Creating new project...")
    project = app.create_project(
        name="Demo Project",
        output_directory="./output",
        auto_captions=True,
        word_by_word_captions=True
    )
    print(f"✅ Project created: {project.name}")
    
    # Check supported formats
    print("\\n📂 Supported formats:")
    formats = app.get_supported_formats()
    for media_type, extensions in formats.items():
        print(f"  {media_type}: {', '.join(extensions)}")
    
    # Validate some files (if they exist)
    test_files = [
        "testing_files/sample_video.mp4",
        "testing_files/sample_audio.mp3",
        "static/Utendo-Bold.ttf"
    ]
    
    print("\\n🔍 Validating test files:")
    for file_path in test_files:
        if os.path.exists(file_path):
            is_valid = app.validate_media_file(file_path)
            print(f"  {file_path}: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            if is_valid:
                # Add to project
                success = app.add_media(file_path)
                if success:
                    print(f"    📁 Added to project")
        else:
            print(f"  {file_path}: ⚠️ File not found")
    
    # Add some overlays
    print("\\n🎨 Adding overlays...")
    
    # Add text overlay
    text_success = app.add_text_overlay(
        text="Welcome to the Demo!",
        start_time=0.0,
        duration=3.0,
        font_size=40,
        font_color="white"
    )
    print(f"  Text overlay: {'✅ Added' if text_success else '❌ Failed'}")
    
    # Add image overlay (if image exists)
    if os.path.exists("static/logo.png"):
        image_success = app.add_image_overlay(
            image_path="static/logo.png",
            start_time=5.0,
            duration=2.0
        )
        print(f"  Image overlay: {'✅ Added' if image_success else '❌ Failed'}")
    
    # Get project info
    print("\\n📊 Project Information:")
    info = app.get_project_info()
    if info:
        print(f"  Name: {info['name']}")
        print(f"  Media files: {info['media_files_count']}")
        print(f"  Timeline items: {info['timeline_items_count']}")
        print(f"  Total duration: {info['total_duration']:.2f}s")
        print(f"  Output path: {info['output_path']}")
    
    # Validate project
    print("\\n🔍 Project Validation:")
    issues = app.validate_project()
    if issues:
        print("  Issues found:")
        for issue in issues:
            print(f"    ⚠️ {issue}")
    else:
        print("  ✅ Project is valid")
    
    # Save project
    print("\\n💾 Saving project...")
    try:
        project_path = app.save_project("demo_project.use_project")
        print(f"✅ Project saved to: {project_path}")
    except Exception as e:
        print(f"❌ Error saving project: {e}")
    
    # Create preview (if we have media)
    if info and info['media_files_count'] > 0:
        print("\\n🎬 Creating preview...")
        try:
            preview_path = app.create_preview(duration=5.0)
            if preview_path:
                print(f"✅ Preview created: {preview_path}")
            else:
                print("❌ Preview creation failed")
        except Exception as e:
            print(f"❌ Preview error: {e}")
    
    # Cleanup
    app.cleanup()
    print("\\n🧹 Cleanup completed")
    print("\\n🎉 Demo completed!")


def demo_service_usage():
    """Demonstrate individual service usage"""
    print("\\n" + "=" * 50)
    print("🔧 Service Usage Demo")
    print("=" * 50)
    
    # Media Service Demo
    print("\\n📁 MediaService Demo:")
    media_service = MediaService()
    
    # Check supported formats
    formats = media_service.get_supported_formats()
    print(f"  Supported video formats: {formats['video'][:3]}...")  # Show first 3
    
    # Project Service Demo
    print("\\n📝 ProjectService Demo:")
    project_service = ProjectService(media_service)
    
    # Create project
    project = project_service.create_project("Service Demo Project")
    print(f"  Created project: {project.name}")
    
    # Export Service Demo
    print("\\n🎬 ExportService Demo:")
    export_service = ExportService()
    print("  Export service initialized")
    
    print("\\n✅ Service demos completed")


def demo_model_usage():
    """Demonstrate model usage"""
    print("\\n" + "=" * 50)
    print("📋 Model Usage Demo")
    print("=" * 50)
    
    # Project Model
    from src.models.project import Project, ProjectSettings
    
    print("\\n📋 Project Model:")
    project = Project(name="Model Demo Project")
    print(f"  Project name: {project.name}")
    print(f"  Created at: {project.created_at}")
    print(f"  Auto captions: {project.settings.auto_captions}")
    
    # Timeline Model
    from src.models.timeline import Timeline, TimelineItem, TimelineItemType
    
    print("\\n⏱️ Timeline Model:")
    timeline = Timeline()
    print(f"  Timeline duration: {timeline.total_duration}s")
    print(f"  Track count: {timeline.track_count}")
    
    # MediaFile Model
    print("\\n📁 MediaFile Model:")
    if os.path.exists("static/Utendo-Bold.ttf"):
        from src.models.media_file import MediaFile, MediaType
        
        try:
            media_file = MediaFile("static/Utendo-Bold.ttf", MediaType.IMAGE)
            print(f"  File: {media_file.metadata.get('filename', 'Unknown')}")
            print(f"  Size: {media_file.metadata.get('size_mb', 0):.2f} MB")
            print(f"  Valid: {media_file.is_valid()}")
        except Exception as e:
            print(f"  Error creating MediaFile: {e}")
    
    print("\\n✅ Model demos completed")


def main():
    """Main demo function"""
    try:
        demo_basic_usage()
        demo_service_usage() 
        demo_model_usage()
        
        print("\\n🎉 All demos completed successfully!")
        print("\\n💡 Next steps:")
        print("  1. Try running: python app_organized.py")
        print("  2. Explore the new architecture in src/")
        print("  3. Read ARCHITECTURE.md for detailed documentation")
        
    except KeyboardInterrupt:
        print("\\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
