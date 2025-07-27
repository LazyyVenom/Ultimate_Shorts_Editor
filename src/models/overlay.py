"""
Overlay Models
Represents different types of overlays (image, text) with timing and positioning
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum


class OverlayType(Enum):
    """Types of overlays"""
    IMAGE = "image"
    TEXT = "text"


class TextAnimation(Enum):
    """Text animation types"""
    NONE = "none"
    FADE = "fade"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    TYPEWRITER = "typewriter"


class Position(Enum):
    """Position presets"""
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


@dataclass
class BaseOverlay:
    """Base class for all overlays"""
    
    start_time: float
    duration: float
    position: Position = field(default=Position.CENTER)
    custom_position: Optional[Tuple[int, int]] = field(default=None)
    opacity: float = field(default=1.0)
    z_index: int = field(default=1)
    
    def get_end_time(self) -> float:
        """Get the end time of the overlay"""
        return self.start_time + self.duration
    
    def is_active_at(self, time: float) -> bool:
        """Check if overlay is active at given time"""
        return self.start_time <= time <= self.get_end_time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'start_time': self.start_time,
            'duration': self.duration,
            'position': self.position.value,
            'custom_position': self.custom_position,
            'opacity': self.opacity,
            'z_index': self.z_index
        }


@dataclass
class ImageOverlay:
    """Image overlay model"""
    
    # Required fields first
    start_time: float
    duration: float
    image_path: str
    
    # Optional fields with defaults
    position: Position = field(default=Position.CENTER)
    custom_position: Optional[Tuple[int, int]] = field(default=None)
    opacity: float = field(default=1.0)
    z_index: int = field(default=1)
    scale: float = field(default=1.0)
    rotation: float = field(default=0.0)
    fit_mode: str = field(default="contain")  # contain, cover, fill, stretch
    
    def get_end_time(self) -> float:
        """Get the end time of the overlay"""
        return self.start_time + self.duration
    
    def is_active_at(self, time: float) -> bool:
        """Check if overlay is active at given time"""
        return self.start_time <= time <= self.get_end_time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': OverlayType.IMAGE.value,
            'start_time': self.start_time,
            'duration': self.duration,
            'position': self.position.value,
            'custom_position': self.custom_position,
            'opacity': self.opacity,
            'z_index': self.z_index,
            'image_path': self.image_path,
            'scale': self.scale,
            'rotation': self.rotation,
            'fit_mode': self.fit_mode
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageOverlay':
        """Create from dictionary"""
        return cls(
            start_time=data['start_time'],
            duration=data['duration'],
            image_path=data['image_path'],
            position=Position(data.get('position', Position.CENTER.value)),
            custom_position=data.get('custom_position'),
            opacity=data.get('opacity', 1.0),
            z_index=data.get('z_index', 1),
            scale=data.get('scale', 1.0),
            rotation=data.get('rotation', 0.0),
            fit_mode=data.get('fit_mode', 'contain')
        )


@dataclass
class TextOverlay:
    """Text overlay model"""
    
    # Required fields first
    start_time: float
    duration: float
    text: str
    
    # Optional fields with defaults
    position: Position = field(default=Position.CENTER)
    custom_position: Optional[Tuple[int, int]] = field(default=None)
    opacity: float = field(default=1.0)
    z_index: int = field(default=1)
    font_path: Optional[str] = field(default=None)
    font_size: int = field(default=32)
    font_color: str = field(default="white")
    background_color: Optional[str] = field(default=None)
    stroke_color: Optional[str] = field(default=None)
    stroke_width: int = field(default=0)
    animation: TextAnimation = field(default=TextAnimation.FADE)
    text_align: str = field(default="center")
    line_spacing: float = field(default=1.2)
    max_width: Optional[int] = field(default=None)
    
    def get_end_time(self) -> float:
        """Get the end time of the overlay"""
        return self.start_time + self.duration
    
    def is_active_at(self, time: float) -> bool:
        """Check if overlay is active at given time"""
        return self.start_time <= time <= self.get_end_time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': OverlayType.TEXT.value,
            'start_time': self.start_time,
            'duration': self.duration,
            'position': self.position.value,
            'custom_position': self.custom_position,
            'opacity': self.opacity,
            'z_index': self.z_index,
            'text': self.text,
            'font_path': self.font_path,
            'font_size': self.font_size,
            'font_color': self.font_color,
            'background_color': self.background_color,
            'stroke_color': self.stroke_color,
            'stroke_width': self.stroke_width,
            'animation': self.animation.value,
            'text_align': self.text_align,
            'line_spacing': self.line_spacing,
            'max_width': self.max_width
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextOverlay':
        """Create from dictionary"""
        return cls(
            start_time=data['start_time'],
            duration=data['duration'],
            text=data['text'],
            position=Position(data.get('position', Position.CENTER.value)),
            custom_position=data.get('custom_position'),
            opacity=data.get('opacity', 1.0),
            z_index=data.get('z_index', 1),
            font_path=data.get('font_path'),
            font_size=data.get('font_size', 32),
            font_color=data.get('font_color', 'white'),
            background_color=data.get('background_color'),
            stroke_color=data.get('stroke_color'),
            stroke_width=data.get('stroke_width', 0),
            animation=TextAnimation(data.get('animation', TextAnimation.FADE.value)),
            text_align=data.get('text_align', 'center'),
            line_spacing=data.get('line_spacing', 1.2),
            max_width=data.get('max_width')
        )
