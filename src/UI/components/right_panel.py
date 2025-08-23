from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSplitter, QSlider,
                             QSpinBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from .video_player import VideoPlayer
from .timeline import Timeline
from .control_bar import ControlBar

class RightPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
    
    def setupUI(self):
        """Setup the right panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create splitter for two rows
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Create video player section (top)
        self.video_player_section = self.createVideoPlayerSection()
        
        # Create control and timeline section (bottom)
        self.control_timeline_section = self.createControlTimelineSection()
        
        # Add sections to splitter
        splitter.addWidget(self.video_player_section)
        splitter.addWidget(self.control_timeline_section)
        
        # Set proportions (60% video player, 40% controls/timeline)
        splitter.setSizes([400, 300])
    
    def createVideoPlayerSection(self):
        """Create video player section"""
        section = QFrame()
        section.setFrameStyle(QFrame.NoFrame)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        title_label = QLabel("Video Preview")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Video player
        self.video_player = VideoPlayer()
        layout.addWidget(self.video_player)
        
        return section
    
    def createControlTimelineSection(self):
        """Create control and timeline section"""
        section = QFrame()
        section.setFrameStyle(QFrame.NoFrame)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Control bar
        self.control_bar = ControlBar()
        layout.addWidget(self.control_bar)
        
        # Timeline
        timeline_label = QLabel("Timeline")
        timeline_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(timeline_label)
        
        self.timeline = Timeline()
        layout.addWidget(self.timeline)
        
        # Connect timeline selection to control bar
        self.timeline.selectionChanged.connect(self.control_bar.updateControlsForSelection)
        
        # Add sample clips for demonstration
        self.timeline.addSampleClips()
        
        return section
