"""
Preview Widget for Ultimate Shorts Editor
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QFrame, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen

from ...models.media_file import MediaFile


class PreviewWidget(QWidget):
    """Widget for previewing video content"""
    
    # Signals
    position_changed = pyqtSignal(float)  # seconds
    play_pause_toggled = pyqtSignal(bool)  # is_playing
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_media: Optional[MediaFile] = None
        self.is_playing = False
        self.current_position = 0.0
        self.duration = 0.0
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Preview")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Preview area
        self.preview_frame = QFrame()
        self.preview_frame.setFrameStyle(QFrame.Box)
        self.preview_frame.setMinimumSize(320, 180)
        self.preview_frame.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.preview_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.preview_frame)
        
        # Preview label (for thumbnails/images)
        preview_layout = QVBoxLayout(self.preview_frame)
        self.preview_label = QLabel("No media loaded")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("color: white; font-size: 12px;")
        preview_layout.addWidget(self.preview_label)
        
        # Position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setMinimum(0)
        self.position_slider.setMaximum(1000)
        self.position_slider.setValue(0)
        self.position_slider.valueChanged.connect(self.on_position_changed)
        layout.addWidget(self.position_slider)
        
        # Time display
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet("font-family: monospace;")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setStyleSheet("font-family: monospace;")
        time_layout.addWidget(self.total_time_label)
        
        layout.addLayout(time_layout)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.play_pause_btn.setEnabled(False)
        controls_layout.addWidget(self.play_pause_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        
        self.previous_frame_btn = QPushButton("◀")
        self.previous_frame_btn.clicked.connect(self.previous_frame)
        self.previous_frame_btn.setEnabled(False)
        controls_layout.addWidget(self.previous_frame_btn)
        
        self.next_frame_btn = QPushButton("▶")
        self.next_frame_btn.clicked.connect(self.next_frame)
        self.next_frame_btn.setEnabled(False)
        controls_layout.addWidget(self.next_frame_btn)
        
        layout.addLayout(controls_layout)
        
    def setup_timer(self):
        """Setup playback timer"""
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_position)
        self.playback_timer.setInterval(33)  # ~30 FPS
        
    def load_media(self, media_file: MediaFile):
        """Load media for preview"""
        self.current_media = media_file
        self.duration = media_file.get_duration()
        self.current_position = 0.0
        
        # Update UI
        self.preview_label.setText(f"Loaded: {media_file.identifier}")
        self.total_time_label.setText(self._format_time(self.duration))
        self.current_time_label.setText("00:00")
        
        # Enable controls for video/audio
        has_duration = self.duration > 0
        self.play_pause_btn.setEnabled(has_duration)
        self.stop_btn.setEnabled(has_duration)
        self.previous_frame_btn.setEnabled(has_duration)
        self.next_frame_btn.setEnabled(has_duration)
        
        # Load thumbnail for video/image
        if media_file.media_type.value in ['video', 'image']:
            self._load_thumbnail()
            
    def _load_thumbnail(self):
        """Load and display thumbnail"""
        if not self.current_media:
            return
            
        try:
            # For images, load directly
            if self.current_media.media_type.value == 'image':
                pixmap = QPixmap(self.current_media.file_path)
                if not pixmap.isNull():
                    # Scale to fit preview area
                    scaled_pixmap = pixmap.scaled(
                        self.preview_frame.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled_pixmap)
                    self.preview_label.setText("")
                    
            # For videos, could extract first frame here
            # This would require additional video processing
            
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            
    def toggle_play_pause(self):
        """Toggle play/pause state"""
        if not self.current_media or self.duration <= 0:
            return
            
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_pause_btn.setText("Pause")
            self.playback_timer.start()
        else:
            self.play_pause_btn.setText("Play")
            self.playback_timer.stop()
            
        self.play_pause_toggled.emit(self.is_playing)
        
    def stop(self):
        """Stop playback"""
        self.is_playing = False
        self.current_position = 0.0
        self.playback_timer.stop()
        self.play_pause_btn.setText("Play")
        self.position_slider.setValue(0)
        self.current_time_label.setText("00:00")
        
    def previous_frame(self):
        """Go to previous frame"""
        if self.duration > 0:
            self.current_position = max(0, self.current_position - 1/30)  # 30fps
            self._update_ui_position()
            
    def next_frame(self):
        """Go to next frame"""
        if self.duration > 0:
            self.current_position = min(self.duration, self.current_position + 1/30)  # 30fps
            self._update_ui_position()
            
    def update_position(self):
        """Update playback position"""
        if self.is_playing and self.duration > 0:
            self.current_position += 0.033  # 33ms
            
            if self.current_position >= self.duration:
                self.stop()
            else:
                self._update_ui_position()
                
    def on_position_changed(self, value: int):
        """Handle position slider change"""
        if self.duration > 0:
            self.current_position = (value / 1000) * self.duration
            self.current_time_label.setText(self._format_time(self.current_position))
            self.position_changed.emit(self.current_position)
            
    def _update_ui_position(self):
        """Update UI elements with current position"""
        if self.duration > 0:
            slider_value = int((self.current_position / self.duration) * 1000)
            self.position_slider.setValue(slider_value)
            self.current_time_label.setText(self._format_time(self.current_position))
            
    def _format_time(self, seconds: float) -> str:
        """Format time as MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def clear_preview(self):
        """Clear the preview"""
        self.current_media = None
        self.duration = 0.0
        self.current_position = 0.0
        self.is_playing = False
        
        # Reset UI
        self.preview_label.setText("No media loaded")
        self.preview_label.setPixmap(QPixmap())
        self.total_time_label.setText("00:00")
        self.current_time_label.setText("00:00")
        self.position_slider.setValue(0)
        self.play_pause_btn.setText("Play")
        self.play_pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.previous_frame_btn.setEnabled(False)
        self.next_frame_btn.setEnabled(False)
        self.playback_timer.stop()
