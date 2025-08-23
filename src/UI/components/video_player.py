from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.is_playing = False
        
    def setupUI(self):
        """Setup video player UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Video display area
        self.video_display = QLabel()
        self.video_display.setMinimumHeight(300)
        self.video_display.setAlignment(Qt.AlignCenter)
        self.video_display.setText("No Video Loaded")
        self.video_display.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: none;
                border-radius: 8px;
                color: #888888;
                font-size: 16px;
            }
        """)
        layout.addWidget(self.video_display)
        
        # Progress bar
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(False)
        layout.addWidget(self.progress_slider)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignCenter)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(50, 40)
        self.play_pause_btn.clicked.connect(self.togglePlayPause)
        controls_layout.addWidget(self.play_pause_btn)
        
        # Stop button
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(50, 40)
        self.stop_btn.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_btn)
        
        # Time labels
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.time_label)
        
        layout.addLayout(controls_layout)
        
        # Apply styles
        self.applyStyles()
    
    def applyStyles(self):
        """Apply dark theme styles to video player components"""
        button_style = """
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #357abd;
            }
            
            QPushButton:pressed {
                background-color: #2968a3;
            }
            
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """
        
        slider_style = """
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                background: #2b2b2b;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #4a90e2;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #357abd;
            }
            
            QSlider::sub-page:horizontal {
                background: #4a90e2;
                border-radius: 4px;
            }
        """
        
        self.play_pause_btn.setStyleSheet(button_style)
        self.stop_btn.setStyleSheet(button_style)
        self.progress_slider.setStyleSheet(slider_style)
        
        self.time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                padding: 5px;
            }
        """)
    
    def togglePlayPause(self):
        """Toggle play/pause state"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start playing video"""
        self.is_playing = True
        self.play_pause_btn.setText("⏸")
        print("Playing video")
    
    def pause(self):
        """Pause video"""
        self.is_playing = False
        self.play_pause_btn.setText("▶")
        print("Pausing video")
    
    def stop(self):
        """Stop video"""
        self.is_playing = False
        self.play_pause_btn.setText("▶")
        self.progress_slider.setValue(0)
        print("Stopping video")
    
    def loadVideo(self, video_path):
        """Load a video file (placeholder)"""
        self.video_display.setText(f"Video: {video_path}")
        self.progress_slider.setEnabled(True)
        print(f"Loading video: {video_path}")
