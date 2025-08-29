from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QLabel, QGroupBox, 
                             QFileDialog, QMessageBox, QSpinBox, QDoubleSpinBox,
                             QListWidgetItem, QSplitter, QScrollArea, QLineEdit,
                             QComboBox, QFrame, QSlider, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette
import os
import time
import platform
import subprocess

class AudioPlayerThread(QThread):
    """Thread for handling audio playback without blocking UI"""
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.process = None
        self._stop_requested = False
    
    def run(self):
        """Run audio playback in separate thread"""
        try:
            system = platform.system()
            if system == "Darwin":
                self.process = subprocess.Popen(["afplay", self.file_path])
            elif system == "Windows":
                self.process = subprocess.Popen(["start", self.file_path], shell=True)
            elif system == "Linux":
                players = ["paplay", "aplay", "mpg123", "ffplay"]
                for player in players:
                    try:
                        self.process = subprocess.Popen([player, self.file_path])
                        break
                    except FileNotFoundError:
                        continue
                else:
                    self.process = subprocess.Popen(["xdg-open", self.file_path])
            
            if self.process:
                self.playback_started.emit()
                # Wait for process to complete or be terminated
                while self.process.poll() is None and not self._stop_requested:
                    self.msleep(100)  # Check every 100ms
                
                if self._stop_requested:
                    self.process.terminate()
                    self.process.wait()
                
                self.playback_finished.emit()
            
        except Exception as e:
            self.playback_error.emit(str(e))
    
    def stop_playback(self):
        """Stop audio playback"""
        self._stop_requested = True
        if self.process:
            try:
                self.process.terminate()
                self.process.wait()
            except:
                pass

class AudioProcessingWorker(QThread):
    """Worker thread for processing audio files"""
    processing_finished = pyqtSignal(str, float)  # file_path, duration
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        # Simulate processing for 2 seconds
        time.sleep(2)
        
        # Try to get real audio duration
        duration = self.get_audio_duration(self.file_path)
        
        self.processing_finished.emit(self.file_path, duration)
    
    def get_audio_duration(self, file_path):
        """Get estimated audio duration using file size"""
        try:
            # Estimate based on file size (rough approximation)
            file_size = os.path.getsize(file_path)
            # Rough estimate: assume ~128 kbps bitrate
            estimated_duration = (file_size * 8) / (128 * 1000)  # Convert to seconds
            # Clamp between reasonable bounds
            estimated_duration = max(10, min(estimated_duration, 1800))  # 10 sec to 30 min
            print(f"Estimated audio duration: {estimated_duration:.1f} seconds")
            return estimated_duration
        except:
            pass
        
        # Fallback: random duration
        import random
        duration = random.uniform(60, 300)
        print(f"Using random duration: {duration:.1f} seconds")
        return duration

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_files = []
        self.primary_video = None
        self.secondary_video = None
        self.image_overlays = []
        self.text_overlays = []
        self.current_video_duration = 0
        self.audio_duration = 0
        self.is_playing = False
        self.processing_worker = None
        self.audio_player_thread = None
        
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
        
        # Playback controls - simplified to just play button and time
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 30)
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setEnabled(False)
        playback_layout.addWidget(self.play_btn)
        
        # Only show total duration after processing
        self.time_label = QLabel("Total Time: 00:00")
        playback_layout.addWidget(self.time_label)
        
        # Add stretch to push elements to the left
        playback_layout.addStretch()
        
        audio_layout.addLayout(playback_layout)
        
        # Audio format info
        format_info = QLabel("Note: Audio playback uses system players and supports all common audio formats.")
        format_info.setStyleSheet("color: #7F8C8D; font-size: 10px; font-style: italic;")
        format_info.setWordWrap(True)
        audio_layout.addWidget(format_info)
        
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
            # Show processing state
            file_name = os.path.basename(file_path)
            self.audio_label.setText(f"Processing: {file_name}...")
            self.audio_label.setStyleSheet("color: #F39C12; font-weight: bold;")
            self.play_btn.setEnabled(False)
            self.timeline_slider.setEnabled(False)
            
            # Start processing in background thread
            self.processing_worker = AudioProcessingWorker(file_path)
            self.processing_worker.processing_finished.connect(self.on_audio_processing_finished)
            self.processing_worker.start()
    
    def on_audio_processing_finished(self, file_path, duration):
        """Called when audio processing is complete"""
        self.audio_files = [file_path]
        self.audio_duration = duration
        self.current_position = 0.0
        
        file_name = os.path.basename(file_path)
        self.audio_label.setText(f"Audio: {file_name}")
        self.audio_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        
        # Enable play button
        self.play_btn.setEnabled(True)
        
        # Update time display to show total duration
        self.update_time_display()
    
    def toggle_playback(self):
        """Toggle audio playback using threaded system"""
        if not self.is_playing:
            # Start playing
            self.play_btn.setText("⏸")
            self.is_playing = True
            
            # Start threaded audio playback
            if self.audio_files:
                # Stop any existing audio thread
                self.stop_audio_thread()
                
                # Create and start new audio player thread
                self.audio_player_thread = AudioPlayerThread(self.audio_files[0])
                self.audio_player_thread.playback_started.connect(self.on_audio_started)
                self.audio_player_thread.playback_finished.connect(self.on_audio_finished)
                self.audio_player_thread.playback_error.connect(self.on_audio_error)
                self.audio_player_thread.start()
                
                print("Starting threaded audio playback...")
            else:
                print("Audio playback simulation (no audio file loaded)")
        else:
            # Pause/Stop playing
            self.play_btn.setText("▶")
            self.is_playing = False
            
            # Stop audio thread
            self.stop_audio_thread()
            print("Audio playback stopped")
    
    def stop_audio_thread(self):
        """Stop the audio player thread if running"""
        if self.audio_player_thread and self.audio_player_thread.isRunning():
            self.audio_player_thread.stop_playback()
            self.audio_player_thread.wait(3000)  # Wait up to 3 seconds
            if self.audio_player_thread.isRunning():
                self.audio_player_thread.terminate()
    
    def on_audio_started(self):
        """Called when audio playback starts"""
        print("Audio playback started successfully")
    
    def on_audio_finished(self):
        """Called when audio playback finishes naturally"""
        if self.is_playing:
            # Audio finished, reset play button
            self.play_btn.setText("▶")
            self.is_playing = False
            print("Audio playback completed")
    
    def on_audio_error(self, error_message):
        """Called when audio playback encounters an error"""
        print(f"Audio playback error: {error_message}")
        if self.is_playing:
            self.play_btn.setText("▶")
            self.is_playing = False
    
    def update_time_display(self):
        """Update the time display label - simplified to show only total time"""
        total_time = self.format_time(self.audio_duration)
        self.time_label.setText(f"Total Time: {total_time}")
    
    def format_time(self, seconds):
        """Format seconds to MM:SS format"""
        if seconds < 0:
            seconds = 0
        seconds = float(seconds)  # Ensure it's a float
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
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
    
    def closeEvent(self, event):
        """Handle window close event - clean up threads"""
        # Stop audio playback and cleanup threads
        if self.is_playing:
            self.is_playing = False
        
        # Stop audio player thread
        self.stop_audio_thread()
        
        # Stop processing worker if running
        if self.processing_worker and self.processing_worker.isRunning():
            self.processing_worker.terminate()
            self.processing_worker.wait(3000)
        
        print("Application cleanup completed")
        event.accept()

