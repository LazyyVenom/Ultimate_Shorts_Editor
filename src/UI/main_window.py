from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QLabel, QGroupBox, 
                             QFileDialog, QMessageBox, QSpinBox, QDoubleSpinBox,
                             QListWidgetItem, QSplitter, QScrollArea, QLineEdit,
                             QComboBox, QFrame, QSlider, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_files = []
        self.primary_video = None
        self.secondary_video = None
        self.image_overlays = []
        self.text_overlays = []
        self.current_video_duration = 0
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Ultimate Shorts Editor")
        self.setGeometry(100, 100, 900, 900)  # Portrait layout
        
        # Central widget with scroll
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)
        
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(15)
        
        # Row 1: Add Audio + Playback Controls
        audio_section = self.create_audio_section()
        main_layout.addWidget(audio_section)
        
        # Row 2: Add Videos (Primary and Secondary columns)
        video_section = self.create_video_section()
        main_layout.addWidget(video_section)
        
        # Row 3: Add Heading
        heading_section = self.create_heading_section()
        main_layout.addWidget(heading_section)
        
        # Row 4: Add Images
        image_section = self.create_image_section()
        main_layout.addWidget(image_section)
        
        # Row 5: Add Text
        text_section = self.create_text_section()
        main_layout.addWidget(text_section)
        
        # Row 6: Generate and Save Button
        generate_section = self.create_generate_section()
        main_layout.addWidget(generate_section)
        
        main_layout.addStretch()
    
    def create_audio_section(self):
        """Row 1: Audio section with playback controls"""
        audio_group = QGroupBox("Audio")
        audio_group.setStyleSheet("QGroupBox::title { font-weight: bold; color: #34495E; }")
        audio_layout = QVBoxLayout(audio_group)
        
        # Audio file selection
        audio_file_layout = QHBoxLayout()
        add_audio_btn = QPushButton("Add Audio File")
        add_audio_btn.clicked.connect(self.add_audio_file)
        audio_file_layout.addWidget(add_audio_btn)
        
        self.audio_label = QLabel("No audio file selected")
        self.audio_label.setStyleSheet("color: #7F8C8D; font-style: italic;")
        audio_file_layout.addWidget(self.audio_label)
        audio_file_layout.addStretch()
        audio_layout.addLayout(audio_file_layout)
        
        # Playback controls
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 30)
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setEnabled(False)
        playback_layout.addWidget(self.play_btn)
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setEnabled(False)
        playback_layout.addWidget(self.timeline_slider)
        
        self.time_label = QLabel("00:00 / 00:00")
        playback_layout.addWidget(self.time_label)
        
        audio_layout.addLayout(playback_layout)
        return audio_group
    
    def create_video_section(self):
        """Row 2: Video section with Primary and Secondary columns"""
        video_group = QGroupBox("Videos")
        video_group.setStyleSheet("QGroupBox::title { font-weight: bold; color: #34495E; }")
        video_layout = QVBoxLayout(video_group)
        
        # Two column layout
        columns_layout = QHBoxLayout()
        
        # Primary Video Column
        primary_column = QVBoxLayout()
        primary_label = QLabel("Primary Video")
        primary_label.setFont(QFont("Arial", 12, QFont.Bold))
        primary_label.setAlignment(Qt.AlignCenter)
        primary_column.addWidget(primary_label)
        
        primary_btn_layout = QHBoxLayout()
        add_primary_btn = QPushButton("Select Primary Video")
        add_primary_btn.clicked.connect(self.add_primary_video)
        primary_btn_layout.addWidget(add_primary_btn)
        
        clear_primary_btn = QPushButton("Clear")
        clear_primary_btn.clicked.connect(self.clear_primary_video)
        primary_btn_layout.addWidget(clear_primary_btn)
        primary_column.addLayout(primary_btn_layout)
        
        self.primary_video_label = QLabel("No primary video selected")
        self.primary_video_label.setStyleSheet("color: #7F8C8D; font-style: italic; padding: 10px; border: 1px solid #BDC3C7; border-radius: 5px; background-color: #F8F9FA;")
        self.primary_video_label.setWordWrap(True)
        self.primary_video_label.setMinimumHeight(60)
        primary_column.addWidget(self.primary_video_label)
        
        # Secondary Video Column
        secondary_column = QVBoxLayout()
        secondary_label = QLabel("Secondary Video")
        secondary_label.setFont(QFont("Arial", 12, QFont.Bold))
        secondary_label.setAlignment(Qt.AlignCenter)
        secondary_column.addWidget(secondary_label)
        
        secondary_btn_layout = QHBoxLayout()
        add_secondary_btn = QPushButton("Select Secondary Video")
        add_secondary_btn.clicked.connect(self.add_secondary_video)
        secondary_btn_layout.addWidget(add_secondary_btn)
        
        clear_secondary_btn = QPushButton("Clear")
        clear_secondary_btn.clicked.connect(self.clear_secondary_video)
        secondary_btn_layout.addWidget(clear_secondary_btn)
        secondary_column.addLayout(secondary_btn_layout)
        
        self.secondary_video_label = QLabel("No secondary video selected")
        self.secondary_video_label.setStyleSheet("color: #7F8C8D; font-style: italic; padding: 10px; border: 1px solid #BDC3C7; border-radius: 5px; background-color: #F8F9FA;")
        self.secondary_video_label.setWordWrap(True)
        self.secondary_video_label.setMinimumHeight(60)
        secondary_column.addWidget(self.secondary_video_label)
        
        columns_layout.addLayout(primary_column)
        columns_layout.addLayout(secondary_column)
        video_layout.addLayout(columns_layout)
        
        return video_group
    
    def create_heading_section(self):
        """Row 3: Heading section"""
        heading_group = QGroupBox("Video Heading")
        heading_group.setStyleSheet("QGroupBox::title { font-weight: bold; color: #34495E; }")
        heading_layout = QVBoxLayout(heading_group)
        
        heading_input_layout = QHBoxLayout()
        heading_input_layout.addWidget(QLabel("Heading Text:"))
        
        self.heading_input = QLineEdit()
        self.heading_input.setPlaceholderText("Enter your video heading...")
        heading_input_layout.addWidget(self.heading_input)
        
        heading_layout.addLayout(heading_input_layout)
        
        return heading_group
    
    def create_image_section(self):
        """Row 4: Image overlays section with scrollable rows"""
        image_group = QGroupBox("Image Overlays")
        image_group.setStyleSheet("QGroupBox::title { font-weight: bold; color: #34495E; }")
        image_layout = QVBoxLayout(image_group)
        
        # Add button
        add_image_btn = QPushButton("+ Add Image Overlay")
        add_image_btn.setStyleSheet("QPushButton { background-color: #3498DB; color: white; font-weight: bold; padding: 8px; }")
        add_image_btn.clicked.connect(self.add_image_overlay)
        image_layout.addWidget(add_image_btn)
        
        # Scrollable area for image rows
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        self.image_scroll_widget = QWidget()
        self.image_scroll_layout = QVBoxLayout(self.image_scroll_widget)
        scroll_area.setWidget(self.image_scroll_widget)
        image_layout.addWidget(scroll_area)
        
        return image_group
    
    def create_text_section(self):
        """Row 5: Text overlays section with scrollable rows"""
        text_group = QGroupBox("Text Overlays")
        text_group.setStyleSheet("QGroupBox::title { font-weight: bold; color: #34495E; }")
        text_layout = QVBoxLayout(text_group)
        
        # Add button
        add_text_btn = QPushButton("+ Add Text Overlay")
        add_text_btn.setStyleSheet("QPushButton { background-color: #9B59B6; color: white; font-weight: bold; padding: 8px; }")
        add_text_btn.clicked.connect(self.add_text_overlay)
        text_layout.addWidget(add_text_btn)
        
        # Scrollable area for text rows
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        self.text_scroll_widget = QWidget()
        self.text_scroll_layout = QVBoxLayout(self.text_scroll_widget)
        scroll_area.setWidget(self.text_scroll_widget)
        text_layout.addWidget(scroll_area)
        
        return text_group
    
    def create_generate_section(self):
        """Row 6: Generate and save button"""
        generate_group = QGroupBox("Export")
        generate_group.setStyleSheet("QGroupBox::title { font-weight: bold; color: #34495E; }")
        generate_layout = QVBoxLayout(generate_group)
        
        # Output path selection
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Path:"))
        
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output location...")
        output_layout.addWidget(self.output_path_input)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output_path)
        output_layout.addWidget(browse_output_btn)
        
        generate_layout.addLayout(output_layout)
        
        # Generate button
        generate_btn = QPushButton("Generate and Save Final Video")
        generate_btn.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-size: 16px; font-weight: bold; padding: 15px; }")
        generate_btn.clicked.connect(self.generate_final_video)
        generate_layout.addWidget(generate_btn)
        
        return generate_group
    
    def add_audio_file(self):
        """Add audio file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.aac *.flac *.m4a *.ogg);;All Files (*)"
        )
        
        if file_path:
            self.audio_files = [file_path]  # Only one audio file for now
            file_name = os.path.basename(file_path)
            self.audio_label.setText(f"Audio: {file_name}")
            self.audio_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            self.play_btn.setEnabled(True)
            self.timeline_slider.setEnabled(True)
    
    def toggle_playback(self):
        """Toggle audio playback"""
        if self.play_btn.text() == "▶":
            self.play_btn.setText("⏸")
            # Add actual playback logic here
        else:
            self.play_btn.setText("▶")
            # Add pause logic here
    
    def add_primary_video(self):
        """Add primary video file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Primary Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm);;All Files (*)"
        )
        
        if file_path:
            self.primary_video = file_path
            file_name = os.path.basename(file_path)
            self.primary_video_label.setText(f"🎬 {file_name}")
            self.primary_video_label.setStyleSheet("color: #27AE60; font-weight: bold; padding: 10px; border: 1px solid #27AE60; border-radius: 5px; background-color: #D5F4E6;")
    
    def add_secondary_video(self):
        """Add secondary video file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Secondary Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm);;All Files (*)"
        )
        
        if file_path:
            self.secondary_video = file_path
            file_name = os.path.basename(file_path)
            self.secondary_video_label.setText(f"🎬 {file_name}")
            self.secondary_video_label.setStyleSheet("color: #2980B9; font-weight: bold; padding: 10px; border: 1px solid #2980B9; border-radius: 5px; background-color: #D6EAF8;")
    
    def clear_primary_video(self):
        """Clear primary video"""
        self.primary_video = None
        self.primary_video_label.setText("No primary video selected")
        self.primary_video_label.setStyleSheet("color: #7F8C8D; font-style: italic; padding: 10px; border: 1px solid #BDC3C7; border-radius: 5px; background-color: #F8F9FA;")
    
    def clear_secondary_video(self):
        """Clear secondary video"""
        self.secondary_video = None
        self.secondary_video_label.setText("No secondary video selected")
        self.secondary_video_label.setStyleSheet("color: #7F8C8D; font-style: italic; padding: 10px; border: 1px solid #BDC3C7; border-radius: 5px; background-color: #F8F9FA;")
    
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
            # Create image overlay row
            overlay_row = self.create_image_overlay_row(file_path)
            self.image_scroll_layout.addWidget(overlay_row)
    
    def create_image_overlay_row(self, image_path):
        """Create a row for image overlay settings"""
        row_frame = QFrame()
        row_frame.setFrameStyle(QFrame.StyledPanel)
        row_frame.setStyleSheet("QFrame { background-color: #F8F9FA; border: 1px solid #E9ECEF; border-radius: 5px; margin: 2px; }")
        
        row_layout = QHBoxLayout(row_frame)
        
        # Image path label
        file_name = os.path.basename(image_path)
        path_label = QLabel(f"📷 {file_name}")
        path_label.setMinimumWidth(150)
        path_label.setStyleSheet("font-weight: bold; color: #495057;")
        row_layout.addWidget(path_label)
        
        # Start time
        start_label = QLabel("Start:")
        start_label.setStyleSheet("color: #495057; font-weight: bold;")
        row_layout.addWidget(start_label)
        
        start_spin = QDoubleSpinBox()
        start_spin.setRange(0, 9999)
        start_spin.setValue(0)
        start_spin.setSingleStep(0.1)
        start_spin.setSuffix("s")
        start_spin.setMinimumWidth(80)
        start_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #CED4DA;
                border-radius: 3px;
                padding: 3px;
                color: #495057;
            }
            QDoubleSpinBox:focus {
                border-color: #80BDFF;
            }
        """)
        row_layout.addWidget(start_spin)
        
        # End time
        end_label = QLabel("End:")
        end_label.setStyleSheet("color: #495057; font-weight: bold;")
        row_layout.addWidget(end_label)
        
        end_spin = QDoubleSpinBox()
        end_spin.setRange(0.1, 9999)
        end_spin.setValue(5.0)
        end_spin.setSingleStep(0.1)
        end_spin.setSuffix("s")
        end_spin.setMinimumWidth(80)
        end_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #CED4DA;
                border-radius: 3px;
                padding: 3px;
                color: #495057;
            }
            QDoubleSpinBox:focus {
                border-color: #80BDFF;
            }
        """)
        row_layout.addWidget(end_spin)
        
        # Padding
        padding_label = QLabel("Padding:")
        padding_label.setStyleSheet("color: #495057; font-weight: bold;")
        row_layout.addWidget(padding_label)
        
        padding_spin = QDoubleSpinBox()
        padding_spin.setRange(0, 50)  # 0% to 50% padding
        padding_spin.setValue(10.0)  # Default 10% padding
        padding_spin.setSingleStep(1.0)
        padding_spin.setSuffix("%")
        padding_spin.setMinimumWidth(80)
        padding_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #CED4DA;
                border-radius: 3px;
                padding: 3px;
                color: #495057;
            }
            QDoubleSpinBox:focus {
                border-color: #80BDFF;
            }
        """)
        row_layout.addWidget(padding_spin)
        
        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(25, 25)
        remove_btn.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-weight: bold; border-radius: 12px; }")
        remove_btn.clicked.connect(lambda: self.remove_image_overlay_row(row_frame, image_path))
        row_layout.addWidget(remove_btn)
        
        # Store overlay data
        overlay_data = {
            'image_path': image_path,
            'start_spin': start_spin,
            'end_spin': end_spin,
            'padding_spin': padding_spin,
            'row_frame': row_frame
        }
        self.image_overlays.append(overlay_data)
        
        return row_frame
    
    def remove_image_overlay_row(self, row_frame, image_path):
        """Remove image overlay row"""
        # Remove from overlays list
        self.image_overlays = [overlay for overlay in self.image_overlays 
                              if overlay['image_path'] != image_path or overlay['row_frame'] != row_frame]
        
        # Remove from layout
        self.image_scroll_layout.removeWidget(row_frame)
        row_frame.deleteLater()
    
    def add_text_overlay(self):
        """Add text overlay"""
        # Create text overlay row
        overlay_row = self.create_text_overlay_row()
        self.text_scroll_layout.addWidget(overlay_row)
    
    def create_text_overlay_row(self):
        """Create a row for text overlay settings"""
        row_frame = QFrame()
        row_frame.setFrameStyle(QFrame.StyledPanel)
        row_frame.setStyleSheet("QFrame { background-color: #F8F9FA; border: 1px solid #E9ECEF; border-radius: 5px; margin: 2px; }")
        
        row_layout = QHBoxLayout(row_frame)
        
        # Text input
        text_label = QLabel("📝 Text:")
        text_label.setStyleSheet("color: #495057; font-weight: bold;")
        row_layout.addWidget(text_label)
        
        text_input = QLineEdit()
        text_input.setPlaceholderText("Enter text...")
        text_input.setMinimumWidth(150)
        text_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #CED4DA;
                border-radius: 3px;
                padding: 5px;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #80BDFF;
                outline: 0;
            }
        """)
        row_layout.addWidget(text_input)
        
        # Start time
        start_label = QLabel("Start:")
        start_label.setStyleSheet("color: #495057; font-weight: bold;")
        row_layout.addWidget(start_label)
        
        start_spin = QDoubleSpinBox()
        start_spin.setRange(0, 9999)
        start_spin.setValue(0)
        start_spin.setSingleStep(0.1)
        start_spin.setSuffix("s")
        start_spin.setMinimumWidth(80)
        start_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #CED4DA;
                border-radius: 3px;
                padding: 3px;
                color: #495057;
            }
            QDoubleSpinBox:focus {
                border-color: #80BDFF;
            }
        """)
        row_layout.addWidget(start_spin)
        
        # End time
        end_label = QLabel("End:")
        end_label.setStyleSheet("color: #495057; font-weight: bold;")
        row_layout.addWidget(end_label)
        
        end_spin = QDoubleSpinBox()
        end_spin.setRange(0.1, 9999)
        end_spin.setValue(3.0)
        end_spin.setSingleStep(0.1)
        end_spin.setSuffix("s")
        end_spin.setMinimumWidth(80)
        end_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #CED4DA;
                border-radius: 3px;
                padding: 3px;
                color: #495057;
            }
            QDoubleSpinBox:focus {
                border-color: #80BDFF;
            }
        """)
        row_layout.addWidget(end_spin)
        
        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(25, 25)
        remove_btn.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-weight: bold; border-radius: 12px; }")
        remove_btn.clicked.connect(lambda: self.remove_text_overlay_row(row_frame))
        row_layout.addWidget(remove_btn)
        
        # Store overlay data
        overlay_data = {
            'text_input': text_input,
            'start_spin': start_spin,
            'end_spin': end_spin,
            'row_frame': row_frame
        }
        self.text_overlays.append(overlay_data)
        
        return row_frame
    
    def remove_text_overlay_row(self, row_frame):
        """Remove text overlay row"""
        # Remove from overlays list
        self.text_overlays = [overlay for overlay in self.text_overlays 
                             if overlay['row_frame'] != row_frame]
        
        # Remove from layout
        self.text_scroll_layout.removeWidget(row_frame)
        row_frame.deleteLater()
    
    def browse_output_path(self):
        """Browse for output file location"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Save Video As",
            "output_video.mp4",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        
        if file_path:
            self.output_path_input.setText(file_path)
    
    def generate_final_video(self):
        """Generate and save the final video"""
        if not self.primary_video and not self.secondary_video:
            QMessageBox.warning(self, "Warning", "Please add at least one video file!")
            return
        
        if not self.output_path_input.text():
            QMessageBox.warning(self, "Warning", "Please specify an output path!")
            return
        
        try:
            # Collect all data
            video_data = {
                'audio_files': self.audio_files,
                'primary_video': self.primary_video,
                'secondary_video': self.secondary_video,
                'heading': {
                    'text': self.heading_input.text()
                },
                'image_overlays': self.get_image_overlay_data(),
                'text_overlays': self.get_text_overlay_data(),
                'output_path': self.output_path_input.text()
            }
            
            from ..utilities.video_processor import VideoProcessor
            
            processor = VideoProcessor()
            
            # Show processing message
            QMessageBox.information(self, "Processing", "Video processing started. This may take a while...")
            
            # Process video with new data structure
            processor.process_video_advanced(video_data)
            
            QMessageBox.information(self, "Success", f"Video processed successfully! Output saved as: {video_data['output_path']}")
            
        except ImportError:
            QMessageBox.warning(self, "Error", "Video processor not implemented yet!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def get_image_overlay_data(self):
        """Get all image overlay data"""
        data = []
        for overlay in self.image_overlays:
            data.append({
                'image_path': overlay['image_path'],
                'start_time': overlay['start_spin'].value(),
                'end_time': overlay['end_spin'].value(),
                'padding': overlay['padding_spin'].value()
            })
        return data
    
    def get_text_overlay_data(self):
        """Get all text overlay data"""
        data = []
        for overlay in self.text_overlays:
            text = overlay['text_input'].text().strip()
            if text:  # Only include non-empty text
                data.append({
                    'text': text,
                    'start_time': overlay['start_spin'].value(),
                    'end_time': overlay['end_spin'].value()
                })
        return data

