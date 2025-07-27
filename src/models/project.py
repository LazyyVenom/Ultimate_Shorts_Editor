"""
Project Model
Main project class that contains all project data and settings
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path
from datetime import datetime

from .media_file import MediaFile, MediaType
from .timeline import Timeline
from .overlay import ImageOverlay, TextOverlay


@dataclass
class ProjectSettings:
    """Project settings and preferences"""
    
    # Output settings
    output_directory: str = ""
    output_filename: str = "output"
    output_format: str = "mp4"
    output_codec: str = "h264"
    output_bitrate: str = "3000k"
    output_fps: int = 30
    output_resolution: tuple[int, int] = field(default=(1080, 1920))  # 9:16 for shorts
    
    # Audio settings
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    audio_sample_rate: int = 44100
    
    # Caption settings
    auto_captions: bool = True
    word_by_word_captions: bool = True
    caption_font_path: str = "static/Utendo-Bold.ttf"
    caption_font_size: int = 32
    caption_font_color: str = "white"
    caption_background_color: Optional[str] = None
    caption_position: str = "bottom"
    
    # Effect settings
    transition_type: str = "crossfade"
    transition_duration: float = 1.0
    color_grading: str = "none"
    stabilization: bool = False
    
    # Processing settings
    quality_preset: str = "medium"  # fast, medium, high
    threads: int = 4
    preview_quality: str = "low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'output_directory': self.output_directory,
            'output_filename': self.output_filename,
            'output_format': self.output_format,
            'output_codec': self.output_codec,
            'output_bitrate': self.output_bitrate,
            'output_fps': self.output_fps,
            'output_resolution': list(self.output_resolution),
            'audio_codec': self.audio_codec,
            'audio_bitrate': self.audio_bitrate,
            'audio_sample_rate': self.audio_sample_rate,
            'auto_captions': self.auto_captions,
            'word_by_word_captions': self.word_by_word_captions,
            'caption_font_path': self.caption_font_path,
            'caption_font_size': self.caption_font_size,
            'caption_font_color': self.caption_font_color,
            'caption_background_color': self.caption_background_color,
            'caption_position': self.caption_position,
            'transition_type': self.transition_type,
            'transition_duration': self.transition_duration,
            'color_grading': self.color_grading,
            'stabilization': self.stabilization,
            'quality_preset': self.quality_preset,
            'threads': self.threads,
            'preview_quality': self.preview_quality
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectSettings':
        """Create from dictionary"""
        settings = cls()
        for key, value in data.items():
            if hasattr(settings, key):
                if key == 'output_resolution' and isinstance(value, list):
                    setattr(settings, key, tuple(value))
                else:
                    setattr(settings, key, value)
        return settings


@dataclass
class Project:
    """Main project class containing all project data"""
    
    # Project metadata
    name: str = "Untitled Project"
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    # Project settings
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    
    # Project data
    timeline: Timeline = field(default_factory=Timeline)
    media_files: Dict[str, MediaFile] = field(default_factory=dict)
    
    # File paths
    project_file_path: Optional[str] = None
    
    def add_media_file(self, file_path: str, media_type: MediaType, 
                      identifier: Optional[str] = None) -> MediaFile:
        """Add a media file to the project"""
        if not identifier:
            identifier = f"{media_type.value}_{len([k for k in self.media_files.keys() 
                                                   if k.startswith(media_type.value)])}"
        
        media_file = MediaFile(file_path, media_type, identifier)
        self.media_files[identifier] = media_file
        self.modified_at = datetime.now()
        return media_file
    
    def remove_media_file(self, identifier: str) -> bool:
        """Remove a media file from the project"""
        if identifier in self.media_files:
            del self.media_files[identifier]
            self.modified_at = datetime.now()
            return True
        return False
    
    def get_media_file(self, identifier: str) -> Optional[MediaFile]:
        """Get a media file by identifier"""
        return self.media_files.get(identifier)
    
    def get_media_files_by_type(self, media_type: MediaType) -> List[MediaFile]:
        """Get all media files of a specific type"""
        return [media for media in self.media_files.values() 
                if media.media_type == media_type]
    
    def add_image_overlay(self, image_path: str, start_time: float, 
                         duration: float, **kwargs) -> ImageOverlay:
        """Add an image overlay to the project"""
        overlay = ImageOverlay(
            image_path=image_path,
            start_time=start_time,
            duration=duration,
            **kwargs
        )
        
        # Add to timeline
        from .timeline import TimelineItem, TimelineItemType
        timeline_item = TimelineItem(
            item_type=TimelineItemType.IMAGE,
            start_time=start_time,
            duration=duration,
            overlay=overlay,
            track_index=2  # Overlay track
        )
        self.timeline.add_item(timeline_item)
        self.modified_at = datetime.now()
        return overlay
    
    def add_text_overlay(self, text: str, start_time: float, 
                        duration: float, **kwargs) -> TextOverlay:
        """Add a text overlay to the project"""
        overlay = TextOverlay(
            text=text,
            start_time=start_time,
            duration=duration,
            **kwargs
        )
        
        # Add to timeline
        from .timeline import TimelineItem, TimelineItemType
        timeline_item = TimelineItem(
            item_type=TimelineItemType.TEXT,
            start_time=start_time,
            duration=duration,
            overlay=overlay,
            track_index=3  # Text track
        )
        self.timeline.add_item(timeline_item)
        self.modified_at = datetime.now()
        return overlay
    
    def get_output_path(self) -> str:
        """Get the full output file path"""
        if not self.settings.output_directory:
            self.settings.output_directory = os.getcwd()
        
        filename = f"{self.settings.output_filename}.{self.settings.output_format}"
        return os.path.join(self.settings.output_directory, filename)
    
    def validate(self) -> List[str]:
        """Validate project and return list of issues"""
        issues = []
        
        # Check for media files
        video_files = self.get_media_files_by_type(MediaType.VIDEO)
        if not video_files:
            issues.append("No video files in project")
        
        # Validate media files
        for identifier, media_file in self.media_files.items():
            if not media_file.is_valid():
                issues.append(f"Invalid media file: {identifier}")
        
        # Check output directory
        if self.settings.output_directory and not os.path.exists(self.settings.output_directory):
            issues.append("Output directory does not exist")
        
        return issues
    
    def save(self, file_path: Optional[str] = None) -> str:
        """Save project to file"""
        if file_path:
            self.project_file_path = file_path
        elif not self.project_file_path:
            # Generate default filename
            safe_name = "".join(c for c in self.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            self.project_file_path = f"{safe_name}.use_project"
        
        self.modified_at = datetime.now()
        
        project_data = self.to_dict()
        with open(self.project_file_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, default=str)
        
        return self.project_file_path
    
    @classmethod
    def load(cls, file_path: str) -> 'Project':
        """Load project from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        project = cls.from_dict(data)
        project.project_file_path = file_path
        return project
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'version': self.version,
            'settings': self.settings.to_dict(),
            'timeline': self.timeline.to_dict(),
            'media_files': {k: v.to_dict() for k, v in self.media_files.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create from dictionary"""
        project = cls(
            name=data.get('name', 'Untitled Project'),
            description=data.get('description', ''),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            modified_at=datetime.fromisoformat(data.get('modified_at', datetime.now().isoformat())),
            version=data.get('version', '1.0')
        )
        
        # Load settings
        if 'settings' in data:
            project.settings = ProjectSettings.from_dict(data['settings'])
        
        # Load timeline
        if 'timeline' in data:
            project.timeline = Timeline.from_dict(data['timeline'])
        
        # Load media files
        if 'media_files' in data:
            for identifier, media_data in data['media_files'].items():
                media_file = MediaFile.from_dict(media_data)
                project.media_files[identifier] = media_file
        
        return project
