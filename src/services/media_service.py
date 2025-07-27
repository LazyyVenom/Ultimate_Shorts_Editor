"""
Media Service
Handles media file operations, validation, and management
"""

import os
import tempfile
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..models.media_file import MediaFile, MediaType


class MediaService:
    """Service for managing media files"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize media service
        
        Args:
            temp_dir: Temporary directory for processing files
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Supported file extensions
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        self.audio_extensions = {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def detect_media_type(self, file_path: str) -> Optional[MediaType]:
        """Detect media type from file extension"""
        if not os.path.exists(file_path):
            return None
        
        extension = Path(file_path).suffix.lower()
        
        if extension in self.video_extensions:
            return MediaType.VIDEO
        elif extension in self.audio_extensions:
            return MediaType.AUDIO
        elif extension in self.image_extensions:
            return MediaType.IMAGE
        
        return None
    
    def validate_media_file(self, file_path: str, media_type: Optional[MediaType] = None) -> bool:
        """Validate a media file
        
        Args:
            file_path: Path to the media file
            media_type: Expected media type (optional, will auto-detect)
            
        Returns:
            True if file is valid
        """
        if not os.path.exists(file_path):
            return False
        
        if not media_type:
            media_type = self.detect_media_type(file_path)
        
        if not media_type:
            return False
        
        try:
            # Create a temporary MediaFile to validate
            media_file = MediaFile(file_path, media_type)
            return media_file.is_valid()
        except Exception as e:
            print(f"Validation error for {file_path}: {e}")
            return False
    
    def get_media_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed media information
        
        Args:
            file_path: Path to the media file
            
        Returns:
            Dictionary with media information or None if invalid
        """
        media_type = self.detect_media_type(file_path)
        if not media_type:
            return None
        
        try:
            media_file = MediaFile(file_path, media_type)
            if media_file.is_valid():
                return media_file.metadata
        except Exception as e:
            print(f"Error getting media info for {file_path}: {e}")
        
        return None
    
    def create_media_file(self, file_path: str, identifier: Optional[str] = None) -> Optional[MediaFile]:
        """Create a MediaFile object with validation
        
        Args:
            file_path: Path to the media file
            identifier: Optional identifier for the media file
            
        Returns:
            MediaFile object or None if invalid
        """
        media_type = self.detect_media_type(file_path)
        if not media_type:
            print(f"Unsupported file type: {file_path}")
            return None
        
        try:
            media_file = MediaFile(file_path, media_type, identifier)
            if media_file.is_valid():
                return media_file
            else:
                print(f"Invalid media file: {file_path}")
                return None
        except Exception as e:
            print(f"Error creating media file for {file_path}: {e}")
            return None
    
    def batch_validate_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """Validate multiple files at once
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.validate_media_file(file_path)
        return results
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get all supported file formats
        
        Returns:
            Dictionary with media types and their supported extensions
        """
        return {
            'video': list(self.video_extensions),
            'audio': list(self.audio_extensions),
            'image': list(self.image_extensions)
        }
    
    def create_preview(self, video_path: str, duration: float = 5.0) -> Optional[str]:
        """Create a preview clip from video
        
        Args:
            video_path: Path to the video file
            duration: Duration of preview in seconds
            
        Returns:
            Path to preview file or None if failed
        """
        if not self.validate_media_file(video_path, MediaType.VIDEO):
            return None
        
        try:
            from moviepy import VideoFileClip
            preview_path = os.path.join(
                self.temp_dir,
                f"preview_{os.path.basename(video_path)}_{int(os.path.getmtime(video_path))}.mp4"
            )
            
            if os.path.exists(preview_path):
                return preview_path
            
            with VideoFileClip(video_path) as video:
                preview_duration = min(duration, video.duration)
                preview = video.subclipped(0, preview_duration)
                
                # Add preview watermark
                from moviepy import TextClip, CompositeVideoClip
                text_clip = TextClip(
                    text="PREVIEW",
                    font_size=30,
                    color='white',
                    font='Arial-Bold'
                ).with_position(('right', 'top')).with_duration(preview_duration)
                
                final_preview = CompositeVideoClip([preview, text_clip])
                final_preview.write_videofile(
                    preview_path,
                    codec='h264',
                    audio_codec='aac',
                    temp_audiofile=os.path.join(self.temp_dir, f'temp_audio_{os.getpid()}.m4a'),
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                
                return preview_path
                
        except Exception as e:
            print(f"Error creating preview for {video_path}: {e}")
            return None
    
    def generate_thumbnail(self, video_path: str, time_offset: Optional[float] = None) -> Optional[str]:
        """Generate thumbnail from video
        
        Args:
            video_path: Path to the video file
            time_offset: Time offset for thumbnail (default: 1/3 of duration)
            
        Returns:
            Path to thumbnail file or None if failed
        """
        if not self.validate_media_file(video_path, MediaType.VIDEO):
            return None
        
        try:
            from moviepy import VideoFileClip
            from PIL import Image
            import numpy as np
            
            thumbnail_path = os.path.join(
                self.temp_dir,
                f"thumb_{os.path.basename(video_path)}_{int(os.path.getmtime(video_path))}.jpg"
            )
            
            if os.path.exists(thumbnail_path):
                return thumbnail_path
            
            with VideoFileClip(video_path) as video:
                if time_offset is None:
                    time_offset = video.duration / 3
                
                frame = video.get_frame(time_offset)
                if frame is not None:
                    image = Image.fromarray(frame)
                    image.save(thumbnail_path, 'JPEG', quality=85)
                    
                    return thumbnail_path
                
        except Exception as e:
            print(f"Error generating thumbnail for {video_path}: {e}")
            return None
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
