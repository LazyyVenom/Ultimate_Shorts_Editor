"""
Project Service
Handles project lifecycle operations and business logic
"""

import os
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from ..models.project import Project, ProjectSettings
from ..models.media_file import MediaFile, MediaType
from ..models.timeline import Timeline, TimelineItem, TimelineItemType
from .media_service import MediaService


class ProjectService:
    """Service for managing video editing projects"""
    
    def __init__(self, media_service: Optional[MediaService] = None):
        """Initialize project service
        
        Args:
            media_service: Media service instance (optional)
        """
        self.media_service = media_service or MediaService()
        self.current_project: Optional[Project] = None
        self.progress_callbacks: Dict[str, Callable] = {}
    
    def create_project(self, name: str = "New Project", **settings) -> Project:
        """Create a new project
        
        Args:
            name: Project name
            **settings: Additional project settings
            
        Returns:
            New Project instance
        """
        project_settings = ProjectSettings()
        
        # Apply any provided settings
        for key, value in settings.items():
            if hasattr(project_settings, key):
                setattr(project_settings, key, value)
        
        self.current_project = Project(
            name=name,
            settings=project_settings,
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        
        print(f"✅ Created new project: {name}")
        return self.current_project
    
    def add_media_to_project(self, file_path: str, identifier: Optional[str] = None) -> Optional[MediaFile]:
        """Add media file to current project
        
        Args:
            file_path: Path to media file
            identifier: Optional identifier
            
        Returns:
            MediaFile instance or None if failed
        """
        if not self.current_project:
            raise ValueError("No project loaded")
        
        # Validate and create media file
        media_file = self.media_service.create_media_file(file_path, identifier)
        if not media_file:
            return None
        
        # Add to project
        identifier = media_file.identifier or f"media_{len(self.current_project.media_files)}"
        self.current_project.media_files[identifier] = media_file
        
        # Auto-add to timeline if it's a video
        if media_file.media_type == MediaType.VIDEO:
            self._auto_add_video_to_timeline(media_file)
        elif media_file.media_type == MediaType.AUDIO:
            self._auto_add_audio_to_timeline(media_file)
        
        self.current_project.modified_at = datetime.now()
        print(f"✅ Added media file: {media_file.identifier}")
        return media_file
    
    def remove_media_from_project(self, identifier: str) -> bool:
        """Remove media file from project
        
        Args:
            identifier: Media file identifier
            
        Returns:
            True if removed successfully
        """
        if not self.current_project:
            raise ValueError("No project loaded")
        
        success = self.current_project.remove_media_file(identifier)
        if success:
            # Remove from timeline as well
            items_to_remove = [
                item for item in self.current_project.timeline.items
                if item.media_file and item.media_file.identifier == identifier
            ]
            for item in items_to_remove:
                self.current_project.timeline.remove_item(item)
            
            print(f"✅ Removed media file: {identifier}")
        
        return success
    
    def add_image_overlay(self, image_path: str, start_time: float, 
                         duration: float, **kwargs) -> bool:
        """Add image overlay to project
        
        Args:
            image_path: Path to image file
            start_time: Start time in seconds
            duration: Duration in seconds
            **kwargs: Additional overlay properties
            
        Returns:
            True if added successfully
        """
        if not self.current_project:
            raise ValueError("No project loaded")
        
        # Validate image file
        if not self.media_service.validate_media_file(image_path, MediaType.IMAGE):
            print(f"❌ Invalid image file: {image_path}")
            return False
        
        try:
            self.current_project.add_image_overlay(image_path, start_time, duration, **kwargs)
            print(f"✅ Added image overlay: {os.path.basename(image_path)}")
            return True
        except Exception as e:
            print(f"❌ Error adding image overlay: {e}")
            return False
    
    def add_text_overlay(self, text: str, start_time: float, 
                        duration: float, **kwargs) -> bool:
        """Add text overlay to project
        
        Args:
            text: Text content
            start_time: Start time in seconds
            duration: Duration in seconds
            **kwargs: Additional overlay properties
            
        Returns:
            True if added successfully
        """
        if not self.current_project:
            raise ValueError("No project loaded")
        
        try:
            self.current_project.add_text_overlay(text, start_time, duration, **kwargs)
            print(f"✅ Added text overlay: {text[:30]}...")
            return True
        except Exception as e:
            print(f"❌ Error adding text overlay: {e}")
            return False
    
    def validate_project(self) -> List[str]:
        """Validate current project
        
        Returns:
            List of validation issues
        """
        if not self.current_project:
            return ["No project loaded"]
        
        return self.current_project.validate()
    
    def get_project_info(self) -> Optional[Dict[str, Any]]:
        """Get comprehensive project information
        
        Returns:
            Project information dictionary or None
        """
        if not self.current_project:
            return None
        
        return {
            'name': self.current_project.name,
            'description': self.current_project.description,
            'created_at': self.current_project.created_at,
            'modified_at': self.current_project.modified_at,
            'media_files_count': len(self.current_project.media_files),
            'timeline_items_count': len(self.current_project.timeline.items),
            'total_duration': self.current_project.timeline.total_duration,
            'validation_issues': self.validate_project(),
            'output_path': self.current_project.get_output_path()
        }
    
    def set_progress_callback(self, callback_name: str, callback: Callable[[int, str], None]):
        """Set progress callback function
        
        Args:
            callback_name: Name of the callback
            callback: Callback function (progress, message)
        """
        self.progress_callbacks[callback_name] = callback
    
    def emit_progress(self, callback_name: str, progress: int, message: str = ""):
        """Emit progress update
        
        Args:
            callback_name: Name of the callback
            progress: Progress percentage (0-100)
            message: Progress message
        """
        if callback_name in self.progress_callbacks:
            self.progress_callbacks[callback_name](progress, message)
    
    def _auto_add_video_to_timeline(self, media_file: MediaFile):
        """Automatically add video to timeline"""
        if not self.current_project:
            return
            
        timeline_item = TimelineItem(
            item_type=TimelineItemType.VIDEO,
            start_time=0.0,
            duration=media_file.get_duration(),
            track_index=0,  # Main video track
            media_file=media_file
        )
        self.current_project.timeline.add_item(timeline_item)
    
    def _auto_add_audio_to_timeline(self, media_file: MediaFile):
        """Automatically add audio to timeline"""
        if not self.current_project:
            return
            
        timeline_item = TimelineItem(
            item_type=TimelineItemType.AUDIO,
            start_time=0.0,
            duration=media_file.get_duration(),
            track_index=1,  # Audio track
            media_file=media_file
        )
        self.current_project.timeline.add_item(timeline_item)
