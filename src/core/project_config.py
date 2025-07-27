"""
Project Configuration Management
Handles project settings, preferences, and configuration validation
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
import os
from pathlib import Path


@dataclass
class ProjectConfig:
    """Configuration class for video editing projects"""
    
    # Basic project info
    project_name: str = "Untitled Project"
    output_directory: str = ""
    
    # Video settings
    primary_video: str = ""
    secondary_video: str = ""
    
    # Audio settings
    overlay_audio: str = ""
    background_audio: str = ""
    
    # Caption settings
    auto_captions: bool = True
    word_by_word: bool = True
    caption_font_path: str = "static/Utendo-Bold.ttf"
    caption_font_size: int = 32
    caption_color: str = "white"
    
    # Effects settings
    transition_type: str = "crossfade"
    transition_duration: float = 1.0
    color_grading: str = "none"
    
    # Output settings
    output_codec: str = "h264"
    output_bitrate: str = "3000k"
    output_fps: int = 30
    
    # Overlay settings
    image_overlays: List[Dict[str, Any]] = field(default_factory=list)
    text_overlays: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()
    
    def validate(self) -> bool:
        """Validate the configuration settings"""
        errors = []
        
        # Check primary video exists
        if self.primary_video and not os.path.exists(self.primary_video):
            errors.append(f"Primary video file not found: {self.primary_video}")
        
        # Check secondary video if specified
        if self.secondary_video and not os.path.exists(self.secondary_video):
            errors.append(f"Secondary video file not found: {self.secondary_video}")
        
        # Check audio files if specified
        if self.overlay_audio and not os.path.exists(self.overlay_audio):
            errors.append(f"Overlay audio file not found: {self.overlay_audio}")
        
        if self.background_audio and not os.path.exists(self.background_audio):
            errors.append(f"Background audio file not found: {self.background_audio}")
        
        # Check font file
        if self.caption_font_path and not os.path.exists(self.caption_font_path):
            print(f"Warning: Font file not found: {self.caption_font_path}")
        
        # Check output directory
        if self.output_directory and not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'project_name': self.project_name,
            'output_directory': self.output_directory,
            'primary_video': self.primary_video,
            'secondary_video': self.secondary_video,
            'overlay_audio': self.overlay_audio,
            'background_audio': self.background_audio,
            'auto_captions': self.auto_captions,
            'word_by_word': self.word_by_word,
            'caption_font_path': self.caption_font_path,
            'caption_font_size': self.caption_font_size,
            'caption_color': self.caption_color,
            'transition_type': self.transition_type,
            'transition_duration': self.transition_duration,
            'color_grading': self.color_grading,
            'output_codec': self.output_codec,
            'output_bitrate': self.output_bitrate,
            'output_fps': self.output_fps,
            'image_overlays': self.image_overlays,
            'text_overlays': self.text_overlays
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Create configuration from dictionary"""
        return cls(**data)
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ProjectConfig':
        """Load configuration from JSON file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def update(self, **kwargs) -> None:
        """Update configuration with new values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")
        
        self.validate()
    
    def get_output_path(self, filename: Optional[str] = None) -> str:
        """Get full output path for a file"""
        if not filename:
            import time
            filename = f"edited_video_{int(time.time())}.mp4"
        
        if self.output_directory:
            return os.path.join(self.output_directory, filename)
        else:
            return filename
