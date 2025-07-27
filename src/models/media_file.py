"""
Media File Model
Represents media files with metadata and validation
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class MediaType(Enum):
    """Media file types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"


@dataclass
class MediaFile:
    """Represents a media file with metadata"""
    
    file_path: str
    media_type: MediaType
    identifier: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    _is_valid: Optional[bool] = None
    
    def __post_init__(self):
        """Initialize after creation"""
        if not self.identifier:
            self.identifier = os.path.basename(self.file_path)
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata for the media file"""
        if not os.path.exists(self.file_path):
            self._is_valid = False
            return
            
        # Basic file info
        self.metadata['filename'] = os.path.basename(self.file_path)
        self.metadata['size_mb'] = os.path.getsize(self.file_path) / (1024 * 1024)
        self.metadata['extension'] = Path(self.file_path).suffix.lower()
        
        try:
            if self.media_type == MediaType.VIDEO:
                self._load_video_metadata()
            elif self.media_type == MediaType.AUDIO:
                self._load_audio_metadata()
            elif self.media_type == MediaType.IMAGE:
                self._load_image_metadata()
            self._is_valid = True
        except Exception as e:
            print(f"Error loading metadata for {self.file_path}: {e}")
            self._is_valid = False
    
    def _load_video_metadata(self) -> None:
        """Load video-specific metadata"""
        try:
            from moviepy import VideoFileClip
            with VideoFileClip(self.file_path) as video:
                self.metadata.update({
                    'duration': video.duration,
                    'width': video.size[0],
                    'height': video.size[1],
                    'fps': video.fps,
                    'has_audio': video.audio is not None,
                    'aspect_ratio': video.size[0] / video.size[1]
                })
        except Exception as e:
            print(f"Error loading video metadata: {e}")
            raise
    
    def _load_audio_metadata(self) -> None:
        """Load audio-specific metadata"""
        try:
            from moviepy import AudioFileClip
            with AudioFileClip(self.file_path) as audio:
                self.metadata.update({
                    'duration': audio.duration,
                    'channels': getattr(audio, 'nchannels', 2),
                    'sample_rate': getattr(audio, 'fps', 44100)
                })
        except Exception as e:
            print(f"Error loading audio metadata: {e}")
            raise
    
    def _load_image_metadata(self) -> None:
        """Load image-specific metadata"""
        try:
            from PIL import Image
            with Image.open(self.file_path) as img:
                self.metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'aspect_ratio': img.width / img.height
                })
        except Exception as e:
            print(f"Error loading image metadata: {e}")
            raise
    
    def is_valid(self) -> bool:
        """Check if media file is valid"""
        if self._is_valid is None:
            self._load_metadata()
        return self._is_valid or False
    
    def get_duration(self) -> float:
        """Get media duration (0 for images)"""
        return self.metadata.get('duration', 0.0)
    
    def get_dimensions(self) -> tuple[int, int]:
        """Get media dimensions"""
        return (
            self.metadata.get('width', 0),
            self.metadata.get('height', 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'file_path': self.file_path,
            'media_type': self.media_type.value,
            'identifier': self.identifier,
            'metadata': self.metadata,
            'is_valid': self.is_valid()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaFile':
        """Create MediaFile from dictionary"""
        return cls(
            file_path=data['file_path'],
            media_type=MediaType(data['media_type']),
            identifier=data.get('identifier'),
            metadata=data.get('metadata', {})
        )
