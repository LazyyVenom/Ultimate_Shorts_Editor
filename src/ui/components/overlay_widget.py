"""
Overlay Widget for Ultimate Shorts Editor
"""

from typing import List, Optional, Union
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QLabel, QGroupBox,
    QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit,
    QComboBox, QFileDialog, QMessageBox, QFormLayout,
    QDialog, QDialogButtonBox
)
from PyQt5.QtCore import pyqtSignal, Qt

from ...models.overlay import ImageOverlay, TextOverlay, OverlayType, Position

# Type alias for overlay union
OverlayUnion = Union[ImageOverlay, TextOverlay]


class OverlayWidget(QWidget):
    """Widget for managing overlays"""
    
    # Signals
    overlay_added = pyqtSignal(object)  # Union type
    overlay_removed = pyqtSignal(str)  # overlay_id
    overlay_modified = pyqtSignal(object)  # Union type
    overlay_selected = pyqtSignal(object)  # Union type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlays: List[OverlayUnion] = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Overlays")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Add overlay buttons
        buttons_layout = QHBoxLayout()
        
        self.add_text_btn = QPushButton("Add Text")
        self.add_text_btn.clicked.connect(self.add_text_overlay)
        buttons_layout.addWidget(self.add_text_btn)
        
        self.add_image_btn = QPushButton("Add Image")
        self.add_image_btn.clicked.connect(self.add_image_overlay)
        buttons_layout.addWidget(self.add_image_btn)
        
        layout.addLayout(buttons_layout)
        
        # Overlay list
        self.overlay_list = QListWidget()
        self.overlay_list.itemClicked.connect(self.on_overlay_selected)
        self.overlay_list.setMinimumHeight(150)
        layout.addWidget(self.overlay_list)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_selected_overlay)
        self.remove_btn.setEnabled(False)
        controls_layout.addWidget(self.remove_btn)
        
        layout.addLayout(controls_layout)
        
        # Overlay info
        self.info_group = QGroupBox("Overlay Information")
        info_layout = QVBoxLayout(self.info_group)
        
        self.info_label = QLabel("No overlay selected")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(self.info_group)
        
    def add_text_overlay(self):
        """Add a text overlay"""
        text, ok = QLineEdit().text(), True  # Simplified for now
        if ok and text:
            overlay = TextOverlay(
                start_time=0.0,
                duration=5.0,
                text=text or "Sample Text",
                position=Position.CENTER
            )
            self.overlays.append(overlay)
            self._refresh_overlay_list()
            self.overlay_added.emit(overlay)
            
    def add_image_overlay(self):
        """Add an image overlay"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;All Files (*)"
        )
        
        if file_path:
            overlay = ImageOverlay(
                start_time=0.0,
                duration=5.0,
                image_path=file_path,
                position=Position.CENTER
            )
            self.overlays.append(overlay)
            self._refresh_overlay_list()
            self.overlay_added.emit(overlay)
            
    def remove_selected_overlay(self):
        """Remove the selected overlay"""
        current_item = self.overlay_list.currentItem()
        if not current_item:
            return
            
        overlay = current_item.data(Qt.ItemDataRole.UserRole)
        if not overlay:
            return
            
        # Remove from list
        self.overlays.remove(overlay)
        self._refresh_overlay_list()
        
        # Clear info
        self.info_label.setText("No overlay selected")
        self.remove_btn.setEnabled(False)
        
        # Emit signal - use a unique id based on properties
        overlay_id = f"{type(overlay).__name__}_{overlay.start_time}_{overlay.duration}"
        self.overlay_removed.emit(overlay_id)
            
    def on_overlay_selected(self, item: QListWidgetItem):
        """Handle overlay selection"""
        overlay = item.data(Qt.ItemDataRole.UserRole)
        if overlay:
            # Update info display
            if isinstance(overlay, TextOverlay):
                info_text = f"""
Type: TEXT
Content: {overlay.text[:50]}{'...' if len(overlay.text) > 50 else ''}
Position: {overlay.position.value}
Start Time: {overlay.start_time:.2f}s
Duration: {overlay.duration:.2f}s
Font Size: {overlay.font_size}px
                """.strip()
            elif isinstance(overlay, ImageOverlay):
                info_text = f"""
Type: IMAGE
Path: {overlay.image_path}
Position: {overlay.position.value}
Start Time: {overlay.start_time:.2f}s
Duration: {overlay.duration:.2f}s
Scale: {overlay.scale}x
                """.strip()
            else:
                info_text = "Unknown overlay type"
            
            self.info_label.setText(info_text)
            self.remove_btn.setEnabled(True)
            
            # Emit signal
            self.overlay_selected.emit(overlay)
            
    def _refresh_overlay_list(self):
        """Refresh the overlay list display"""
        self.overlay_list.clear()
        
        for i, overlay in enumerate(self.overlays):
            if isinstance(overlay, TextOverlay):
                display_text = f"{i+1}. TEXT: {overlay.text[:30]}"
                if len(overlay.text) > 30:
                    display_text += "..."
            elif isinstance(overlay, ImageOverlay):
                import os
                filename = os.path.basename(overlay.image_path)
                display_text = f"{i+1}. IMAGE: {filename}"
            else:
                display_text = f"{i+1}. UNKNOWN"
                
            display_text += f" ({overlay.start_time:.1f}s - {overlay.start_time + overlay.duration:.1f}s)"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, overlay)
            self.overlay_list.addItem(item)
            
    def get_overlays(self) -> List[OverlayUnion]:
        """Get all overlays"""
        return self.overlays.copy()
        
    def clear_overlays(self):
        """Clear all overlays"""
        self.overlays.clear()
        self.overlay_list.clear()
        self.info_label.setText("No overlay selected")
        self.remove_btn.setEnabled(False)
        
    def load_overlays(self, overlays: List[OverlayUnion]):
        """Load overlays into the widget"""
        self.overlays = overlays.copy()
        self._refresh_overlay_list()
