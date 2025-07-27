"""
Media Input Widget for Ultimate Shorts Editor
"""

from typing import Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QLabel, QGroupBox,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon

from ...models.media_file import MediaFile, MediaType


class MediaInputWidget(QWidget):
    """Widget for handling media file input and management"""
    
    # Signals
    media_added = pyqtSignal(MediaFile)
    media_removed = pyqtSignal(str)  # file_path
    media_selected = pyqtSignal(MediaFile)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_files: List[MediaFile] = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Media Files")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Add buttons section
        buttons_layout = QHBoxLayout()
        
        self.add_video_btn = QPushButton("Add Video")
        self.add_video_btn.clicked.connect(self.add_video_file)
        buttons_layout.addWidget(self.add_video_btn)
        
        self.add_audio_btn = QPushButton("Add Audio")
        self.add_audio_btn.clicked.connect(self.add_audio_file)
        buttons_layout.addWidget(self.add_audio_btn)
        
        self.add_image_btn = QPushButton("Add Image")
        self.add_image_btn.clicked.connect(self.add_image_file)
        buttons_layout.addWidget(self.add_image_btn)
        
        layout.addLayout(buttons_layout)
        
        # Media list
        self.media_list = QListWidget()
        self.media_list.itemClicked.connect(self.on_media_selected)
        self.media_list.setMinimumHeight(200)
        layout.addWidget(self.media_list)
        
        # Remove button
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected_media)
        self.remove_btn.setEnabled(False)
        layout.addWidget(self.remove_btn)
        
        # Media info section
        self.info_group = QGroupBox("Media Information")
        info_layout = QVBoxLayout(self.info_group)
        
        self.info_label = QLabel("No media selected")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(self.info_group)
        
    def add_video_file(self):
        """Add a video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm);;All Files (*)"
        )
        
        if file_path:
            self._add_media_file(file_path, MediaType.VIDEO)
            
    def add_audio_file(self):
        """Add an audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.aac *.flac *.ogg *.m4a);;All Files (*)"
        )
        
        if file_path:
            self._add_media_file(file_path, MediaType.AUDIO)
            
    def add_image_file(self):
        """Add an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;All Files (*)"
        )
        
        if file_path:
            self._add_media_file(file_path, MediaType.IMAGE)
            
    def _add_media_file(self, file_path: str, media_type: MediaType):
        """Add a media file to the list"""
        try:
            # Check if file already exists
            if any(media.file_path == file_path for media in self.media_files):
                QMessageBox.warning(self, "Warning", "This file is already added!")
                return
                
            # Create MediaFile object
            media_file = MediaFile(file_path=file_path, media_type=media_type)
            
            # Add to list
            self.media_files.append(media_file)
            
            # Add to UI list
            item = QListWidgetItem(f"{media_type.value.upper()}: {media_file.identifier}")
            item.setData(Qt.ItemDataRole.UserRole, media_file)
            self.media_list.addItem(item)
            
            # Emit signal
            self.media_added.emit(media_file)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add media file: {str(e)}")
            
    def remove_selected_media(self):
        """Remove the selected media file"""
        current_item = self.media_list.currentItem()
        if not current_item:
            return
            
        media_file = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Remove from list
        self.media_files.remove(media_file)
        
        # Remove from UI
        row = self.media_list.row(current_item)
        self.media_list.takeItem(row)
        
        # Emit signal
        self.media_removed.emit(media_file.file_path)
        
        # Clear info if this was selected
        self.info_label.setText("No media selected")
        self.remove_btn.setEnabled(False)
        
    def on_media_selected(self, item: QListWidgetItem):
        """Handle media selection"""
        media_file = item.data(Qt.ItemDataRole.UserRole)
        if media_file:
            # Update info display
            info_text = f"""
Name: {media_file.identifier}
Type: {media_file.media_type.value.upper()}
Path: {media_file.file_path}
Size: {media_file.metadata.get('size_mb', 0):.2f} MB
Duration: {media_file.get_duration():.2f}s
            """.strip()
            
            if media_file.metadata:
                width = media_file.metadata.get('width')
                height = media_file.metadata.get('height')
                if width and height:
                    info_text += f"\nResolution: {width}x{height}"
                fps = media_file.metadata.get('fps')
                if fps:
                    info_text += f"\nFPS: {fps}"
                bitrate = media_file.metadata.get('bitrate')
                if bitrate:
                    info_text += f"\nBitrate: {bitrate}"
                    
            self.info_label.setText(info_text)
            self.remove_btn.setEnabled(True)
            
            # Emit signal
            self.media_selected.emit(media_file)
            
    def get_media_files(self) -> List[MediaFile]:
        """Get all media files"""
        return self.media_files.copy()
        
    def clear_media_files(self):
        """Clear all media files"""
        self.media_files.clear()
        self.media_list.clear()
        self.info_label.setText("No media selected")
        self.remove_btn.setEnabled(False)
        
    def get_media_by_type(self, media_type: MediaType) -> List[MediaFile]:
        """Get media files by type"""
        return [media for media in self.media_files if media.media_type == media_type]
