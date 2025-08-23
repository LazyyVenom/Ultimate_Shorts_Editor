from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QLabel, QGroupBox, 
                             QFileDialog, QMessageBox, QSpinBox, QDoubleSpinBox,
                             QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_files = []
        self.image_overlays = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Ultimate Shorts Editor")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Ultimate Shorts Editor")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create splitter for video and image sections
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Video section
        video_group = self.create_video_section()
        splitter.addWidget(video_group)
        
        # Image overlay section
        image_group = self.create_image_section()
        splitter.addWidget(image_group)
        
        # Process button
        process_btn = QPushButton("Process Video")
        process_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 14px; padding: 10px; }")
        process_btn.clicked.connect(self.process_video)
        main_layout.addWidget(process_btn)
    
    def create_video_section(self):
        """Create the video files section"""
        video_group = QGroupBox("Video Files (Will be concatenated)")
        video_layout = QVBoxLayout(video_group)
        
        # Buttons layout
        video_btn_layout = QHBoxLayout()
        
        add_video_btn = QPushButton("Add Video Files")
        add_video_btn.clicked.connect(self.add_video_files)
        video_btn_layout.addWidget(add_video_btn)
        
        clear_videos_btn = QPushButton("Clear All")
        clear_videos_btn.clicked.connect(self.clear_videos)
        video_btn_layout.addWidget(clear_videos_btn)
        
        remove_video_btn = QPushButton("Remove Selected")
        remove_video_btn.clicked.connect(self.remove_selected_video)
        video_btn_layout.addWidget(remove_video_btn)
        
        video_layout.addLayout(video_btn_layout)
        
        # Video list
        self.video_list = QListWidget()
        self.video_list.setMinimumHeight(200)
        video_layout.addWidget(self.video_list)
        
        # Video info
        video_info_label = QLabel("Videos will be concatenated in the order shown above")
        video_info_label.setStyleSheet("color: #666; font-style: italic;")
        video_layout.addWidget(video_info_label)
        
        return video_group
    
    def create_image_section(self):
        """Create the image overlay section"""
        image_group = QGroupBox("Image Overlays")
        image_layout = QVBoxLayout(image_group)
        
        # Buttons layout
        image_btn_layout = QHBoxLayout()
        
        add_image_btn = QPushButton("Add Image Overlay")
        add_image_btn.clicked.connect(self.add_image_overlay)
        image_btn_layout.addWidget(add_image_btn)
        
        clear_images_btn = QPushButton("Clear All")
        clear_images_btn.clicked.connect(self.clear_images)
        image_btn_layout.addWidget(clear_images_btn)
        
        remove_image_btn = QPushButton("Remove Selected")
        remove_image_btn.clicked.connect(self.remove_selected_image)
        image_btn_layout.addWidget(remove_image_btn)
        
        image_layout.addLayout(image_btn_layout)
        
        # Image list
        self.image_list = QListWidget()
        self.image_list.setMinimumHeight(200)
        image_layout.addWidget(self.image_list)
        
        # Image info
        image_info_label = QLabel("Images will be overlaid at specified times")
        image_info_label.setStyleSheet("color: #666; font-style: italic;")
        image_layout.addWidget(image_info_label)
        
        return image_group
    
    def add_video_files(self):
        """Add video files for concatenation"""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm);;All Files (*)"
        )
        
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.video_files:
                    self.video_files.append(file_path)
                    file_name = os.path.basename(file_path)
                    self.video_list.addItem(f"{len(self.video_files)}. {file_name}")
    
    def add_image_overlay(self):
        """Add image overlay with timing"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff);;All Files (*)"
        )
        
        if file_path:
            # Create a dialog to get overlay settings
            dialog = ImageOverlayDialog(self, file_path)
            if dialog.exec_():
                overlay_data = dialog.get_overlay_data()
                self.image_overlays.append(overlay_data)
                
                file_name = os.path.basename(file_path)
                display_text = f"{file_name} (Start: {overlay_data['start_time']}s, Duration: {overlay_data['duration']}s)"
                self.image_list.addItem(display_text)
    
    def clear_videos(self):
        """Clear all video files"""
        self.video_files.clear()
        self.video_list.clear()
    
    def clear_images(self):
        """Clear all image overlays"""
        self.image_overlays.clear()
        self.image_list.clear()
    
    def remove_selected_video(self):
        """Remove selected video file"""
        current_row = self.video_list.currentRow()
        if current_row >= 0:
            self.video_files.pop(current_row)
            self.video_list.takeItem(current_row)
            # Update numbering
            self.refresh_video_list()
    
    def remove_selected_image(self):
        """Remove selected image overlay"""
        current_row = self.image_list.currentRow()
        if current_row >= 0:
            self.image_overlays.pop(current_row)
            self.image_list.takeItem(current_row)
    
    def refresh_video_list(self):
        """Refresh video list with updated numbering"""
        self.video_list.clear()
        for i, file_path in enumerate(self.video_files):
            file_name = os.path.basename(file_path)
            self.video_list.addItem(f"{i+1}. {file_name}")
    
    def process_video(self):
        """Process the video with concatenation and overlays"""
        if not self.video_files:
            QMessageBox.warning(self, "Warning", "Please add at least one video file!")
            return
        
        try:
            from ..utilities.video_processor import VideoProcessor
            
            processor = VideoProcessor()
            output_path = "output_video.mp4"
            
            # Show processing message
            QMessageBox.information(self, "Processing", "Video processing started. This may take a while...")
            
            # Process video
            processor.process_video(self.video_files, self.image_overlays, output_path)
            
            QMessageBox.information(self, "Success", f"Video processed successfully! Output saved as: {output_path}")
            
        except ImportError:
            QMessageBox.warning(self, "Error", "Video processor not implemented yet!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class ImageOverlayDialog(QWidget):
    def __init__(self, parent, image_path):
        super().__init__()
        self.parent = parent
        self.image_path = image_path
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Image Overlay Settings")
        self.setGeometry(200, 200, 400, 200)
        
        layout = QVBoxLayout(self)
        
        # Image path display
        path_label = QLabel(f"Image: {os.path.basename(self.image_path)}")
        path_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(path_label)
        
        # Start time
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Time (seconds):"))
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0, 9999)
        self.start_time_spin.setValue(0)
        self.start_time_spin.setSingleStep(0.1)
        start_layout.addWidget(self.start_time_spin)
        layout.addLayout(start_layout)
        
        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (seconds):"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 9999)
        self.duration_spin.setValue(5.0)
        self.duration_spin.setSingleStep(0.1)
        duration_layout.addWidget(self.duration_spin)
        layout.addLayout(duration_layout)
        
        # Position (optional for future enhancement)
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:"))
        self.position_combo = QPushButton("Center (Click to change)")
        self.position_combo.clicked.connect(self.change_position)
        self.position = "center"
        position_layout.addWidget(self.position_combo)
        layout.addLayout(position_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def change_position(self):
        positions = ["center", "top-left", "top-right", "bottom-left", "bottom-right"]
        current_index = positions.index(self.position) if self.position in positions else 0
        next_index = (current_index + 1) % len(positions)
        self.position = positions[next_index]
        self.position_combo.setText(f"{self.position.title()} (Click to change)")
    
    def get_overlay_data(self):
        return {
            'image_path': self.image_path,
            'start_time': self.start_time_spin.value(),
            'duration': self.duration_spin.value(),
            'position': self.position
        }
    
    def exec_(self):
        self.show()
        return True
    
    def accept(self):
        self.hide()
    
    def reject(self):
        self.hide()
