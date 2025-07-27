"""
Timeline Models
Represents the video timeline and timeline items
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from .media_file import MediaFile
from .overlay import BaseOverlay, ImageOverlay, TextOverlay


class TimelineItemType(Enum):
    """Types of timeline items"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    EFFECT = "effect"


@dataclass
class TimelineItem:
    """Represents an item on the timeline"""
    
    item_type: TimelineItemType
    start_time: float
    duration: float
    track_index: int = 0
    media_file: Optional[MediaFile] = None
    overlay: Optional[Union[BaseOverlay, ImageOverlay, TextOverlay]] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def get_end_time(self) -> float:
        """Get the end time of the timeline item"""
        return self.start_time + self.duration
    
    def overlaps_with(self, other: 'TimelineItem') -> bool:
        """Check if this item overlaps with another item"""
        if self.track_index != other.track_index:
            return False
        
        return not (self.get_end_time() <= other.start_time or 
                   other.get_end_time() <= self.start_time)
    
    def is_active_at(self, time: float) -> bool:
        """Check if item is active at given time"""
        return self.enabled and self.start_time <= time <= self.get_end_time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            'item_type': self.item_type.value,
            'start_time': self.start_time,
            'duration': self.duration,
            'track_index': self.track_index,
            'properties': self.properties,
            'enabled': self.enabled
        }
        
        if self.media_file:
            data['media_file'] = self.media_file.to_dict()
        
        if self.overlay:
            data['overlay'] = self.overlay.to_dict()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineItem':
        """Create from dictionary"""
        item = cls(
            item_type=TimelineItemType(data['item_type']),
            start_time=data['start_time'],
            duration=data['duration'],
            track_index=data.get('track_index', 0),
            properties=data.get('properties', {}),
            enabled=data.get('enabled', True)
        )
        
        if 'media_file' in data:
            item.media_file = MediaFile.from_dict(data['media_file'])
        
        if 'overlay' in data:
            overlay_data = data['overlay']
            if overlay_data.get('type') == 'image':
                item.overlay = ImageOverlay.from_dict(overlay_data)
            elif overlay_data.get('type') == 'text':
                item.overlay = TextOverlay.from_dict(overlay_data)
        
        return item


@dataclass
class Timeline:
    """Represents the video timeline with multiple tracks"""
    
    items: List[TimelineItem] = field(default_factory=list)
    total_duration: float = 0.0
    track_count: int = 4  # Default: video, audio, overlay, text
    
    def add_item(self, item: TimelineItem) -> None:
        """Add an item to the timeline"""
        self.items.append(item)
        self._update_duration()
    
    def remove_item(self, item: TimelineItem) -> None:
        """Remove an item from the timeline"""
        if item in self.items:
            self.items.remove(item)
            self._update_duration()
    
    def get_items_at_time(self, time: float) -> List[TimelineItem]:
        """Get all active items at a specific time"""
        return [item for item in self.items if item.is_active_at(time)]
    
    def get_items_by_track(self, track_index: int) -> List[TimelineItem]:
        """Get all items on a specific track"""
        return [item for item in self.items if item.track_index == track_index]
    
    def get_items_by_type(self, item_type: TimelineItemType) -> List[TimelineItem]:
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]
    
    def get_overlapping_items(self, item: TimelineItem) -> List[TimelineItem]:
        """Get all items that overlap with the given item"""
        return [other for other in self.items 
                if other != item and item.overlaps_with(other)]
    
    def _update_duration(self) -> None:
        """Update the total timeline duration"""
        if self.items:
            self.total_duration = max(item.get_end_time() for item in self.items)
        else:
            self.total_duration = 0.0
    
    def clear(self) -> None:
        """Clear all items from the timeline"""
        self.items.clear()
        self.total_duration = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'items': [item.to_dict() for item in self.items],
            'total_duration': self.total_duration,
            'track_count': self.track_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Timeline':
        """Create from dictionary"""
        timeline = cls(
            total_duration=data.get('total_duration', 0.0),
            track_count=data.get('track_count', 4)
        )
        
        for item_data in data.get('items', []):
            timeline.add_item(TimelineItem.from_dict(item_data))
        
        return timeline
