"""
Media Manager
Handles media file operations, validation, and metadata extraction
"""

import os
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import tempfile
import shutil
from moviepy import VideoFileClip, AudioFileClip
from PIL import Image


class MediaFile:
    """Represents a media file with metadata"""
    
    def __init__(self, file_path: str, media_type: str):
        self.file_path = file_path
        self.media_type = media_type  # 'video', 'audio', 'image'
        self.metadata: Dict[str, Any] = {}
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata for the media file"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Media file not found: {self.file_path}")
        
        # Basic file info
        self.metadata['filename'] = os.path.basename(self.file_path)
        self.metadata['size_mb'] = os.path.getsize(self.file_path) / (1024 * 1024)
        
        try:
            if self.media_type == 'video':
                self._load_video_metadata()
            elif self.media_type == 'audio':
                self._load_audio_metadata()
            elif self.media_type == 'image':
                self._load_image_metadata()
        except Exception as e:
            print(f"Warning: Could not load metadata for {self.file_path}: {e}")
    
    def _load_video_metadata(self) -> None:
        """Load video-specific metadata"""
        video = None
        try:
            video = VideoFileClip(self.file_path)
            self.metadata.update({
                'duration': video.duration,
                'width': video.size[0],
                'height': video.size[1],
                'fps': video.fps,
                'has_audio': video.audio is not None,
                'aspect_ratio': video.size[0] / video.size[1]
            })
        finally:
            if video:
                video.close()
    
    def _load_audio_metadata(self) -> None:
        """Load audio-specific metadata"""
        audio = None
        try:
            audio = AudioFileClip(self.file_path)
            self.metadata.update({
                'duration': audio.duration,
                'fps': audio.fps if hasattr(audio, 'fps') else None
            })
        finally:
            if audio:
                audio.close()
    
    def _load_image_metadata(self) -> None:
        """Load image-specific metadata"""
        try:
            with Image.open(self.file_path) as img:
                self.metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'aspect_ratio': img.width / img.height
                })
        except Exception as e:
            print(f"Error loading image metadata: {e}")
    
    def is_valid(self) -> bool:
        """Check if the media file is valid and accessible"""
        return os.path.exists(self.file_path) and bool(self.metadata)
    
    def get_duration(self) -> Optional[float]:
        """Get duration for video/audio files"""
        return self.metadata.get('duration')
    
    def get_dimensions(self) -> Optional[tuple]:
        """Get dimensions for video/image files"""
        width = self.metadata.get('width')
        height = self.metadata.get('height')
        if width and height:
            return (width, height)
        return None


class MediaManager:
    """Manages media files and operations"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.media_files: Dict[str, MediaFile] = {}
        self._ensure_temp_dir()
    
    def _ensure_temp_dir(self) -> None:
        """Ensure temporary directory exists"""
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def add_media_file(self, file_path: str, media_type: str, identifier: Optional[str] = None) -> MediaFile:
        """Add a media file to the manager"""
        if not identifier:
            identifier = os.path.basename(file_path)
        
        media_file = MediaFile(file_path, media_type)
        self.media_files[identifier] = media_file
        return media_file
    
    def get_media_file(self, identifier: str) -> Optional[MediaFile]:
        """Get a media file by identifier"""
        return self.media_files.get(identifier)
    
    def validate_video_file(self, file_path: str) -> bool:
        """Validate a video file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            video = VideoFileClip(file_path)
            # Basic validation: has duration and size
            is_valid = video.duration > 0 and video.size[0] > 0 and video.size[1] > 0
            video.close()
            return is_valid
        except Exception:
            return False
    
    def validate_audio_file(self, file_path: str) -> bool:
        """Validate an audio file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            audio = AudioFileClip(file_path)
            # Basic validation: has duration
            is_valid = audio.duration > 0
            audio.close()
            return is_valid
        except Exception:
            return False
    
    def validate_image_file(self, file_path: str) -> bool:
        """Validate an image file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with Image.open(file_path) as img:
                # Basic validation: has dimensions
                return img.width > 0 and img.height > 0
        except Exception:
            return False
    
    def get_video_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive video information"""
        if not self.validate_video_file(file_path):
            return None
        
        video = None
        try:
            video = VideoFileClip(file_path)
            info = {
                'duration': video.duration,
                'width': video.size[0],
                'height': video.size[1],
                'fps': video.fps,
                'audio': video.audio is not None,
                'filename': os.path.basename(file_path),
                'filesize_mb': os.path.getsize(file_path) / (1024 * 1024),
                'aspect_ratio': video.size[0] / video.size[1]
            }
            return info
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
        finally:
            if video:
                video.close()
    
    def create_preview(self, video_path: str, duration: float = 5) -> Optional[str]:
        """Create a preview clip from video"""
        if not self.validate_video_file(video_path):
            return None
        
        preview_path = os.path.join(
            self.temp_dir, 
            f"preview_{os.path.basename(video_path)}_{int(os.path.getmtime(video_path))}.mp4"
        )
        
        video = None
        preview = None
        try:
            video = VideoFileClip(video_path)
            preview_duration = min(duration, video.duration)
            preview = video.subclipped(0, preview_duration)
            
            # Add preview watermark
            from moviepy import TextClip, CompositeVideoClip
            try:
                text_clip = TextClip(
                    text="PREVIEW",
                    font_size=24,
                    color='white'
                ).with_position(('right', 'top')).with_duration(preview_duration)
                
                preview = CompositeVideoClip([preview, text_clip])
            except Exception:
                pass  # Continue without watermark if text fails
            
            preview.write_videofile(
                preview_path,
                codec="h264",
                audio_codec="aac",
                bitrate="1500k",
                fps=30,
                logger=None
            )
            
            return preview_path
            
        except Exception as e:
            print(f"Error creating preview: {e}")
            return None
        finally:
            if video:
                video.close()
            if preview:
                preview.close()
    
    def generate_thumbnail(self, video_path: str, output_path: Optional[str] = None, text: Optional[str] = None) -> Optional[str]:
        """Generate a thumbnail from video"""
        if not self.validate_video_file(video_path):
            return None
        
        if not output_path:
            output_path = os.path.join(
                self.temp_dir,
                f"thumb_{os.path.splitext(os.path.basename(video_path))[0]}.jpg"
            )
        
        video = None
        try:
            video = VideoFileClip(video_path)
            thumbnail_time = video.duration / 3  # 1/3 into the video
            frame = video.get_frame(thumbnail_time)
            
            if frame is not None:
                img = Image.fromarray(frame)
                
                if text:
                    from PIL import ImageDraw, ImageFont
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype("static/Utendo-Bold.ttf", size=40)
                    except Exception:
                        font = ImageFont.load_default()
                    
                    # Calculate text position
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    position = ((img.width - text_width) // 2, (img.height - text_height) // 2)
                    
                    # Add outline
                    outline_color = (0, 0, 0)
                    text_color = (255, 255, 255)
                    
                    for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        draw.text((position[0] + offset[0], position[1] + offset[1]), 
                                text, font=font, fill=outline_color)
                    
                    draw.text(position, text, font=font, fill=text_color)
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                img.save(output_path, quality=95)
                return output_path
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
        finally:
            if video:
                video.close()
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                    except Exception as e:
                        print(f"Warning: Could not delete temp file {file_path}: {e}")
        except Exception as e:
            print(f"Warning: Could not cleanup temp directory: {e}")
    
    def copy_to_temp(self, file_path: str) -> str:
        """Copy a file to temp directory and return new path"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        temp_path = os.path.join(self.temp_dir, filename)
        shutil.copy2(file_path, temp_path)
        return temp_path
