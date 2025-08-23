from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush

class TimelineTrack(QWidget):
    """Individual timeline track for different media types"""
    
    trackClicked = pyqtSignal(str, str)  # track_type, track_name
    
    def __init__(self, track_type, track_name, color):
        super().__init__()
        self.track_type = track_type  # 'video', 'audio', 'image', 'text'
        self.track_name = track_name
        self.color = color
        self.clips = []  # List of clips on this track
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        
    def addClip(self, clip_data):
        """Add a clip to this track"""
        self.clips.append(clip_data)
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event for timeline track"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw track background
        track_rect = self.rect()
        painter.fillRect(track_rect, QColor("#2b2b2b"))
        
        # Draw clips
        clip_width = 100  # Fixed width for demo
        x_offset = 10
        
        for i, clip in enumerate(self.clips):
            clip_rect = QRect(x_offset + (i * (clip_width + 5)), 5, clip_width, 30)
            
            # Draw clip background
            painter.fillRect(clip_rect, QColor(self.color))
            
            # Draw clip text
            painter.setPen(QPen(QColor("#ffffff")))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(clip_rect, Qt.AlignCenter, clip.get('name', f'Clip {i+1}'))
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on track"""
        if event.button() == Qt.LeftButton:
            self.trackClicked.emit(self.track_type, self.track_name)
            print(f"Track clicked: {self.track_type} - {self.track_name}")

class Timeline(QWidget):
    """Main timeline widget containing all tracks"""
    
    selectionChanged = pyqtSignal(str, dict)  # selection_type, selection_data
    
    def __init__(self):
        super().__init__()
        self.tracks = {}
        self.setupUI()
        self.createDefaultTracks()
    
    def setupUI(self):
        """Setup timeline UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Timeline header with time markers
        self.createTimelineHeader(layout)
        
        # Scrollable area for tracks
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(200)
        
        # Track container
        self.track_container = QWidget()
        self.track_layout = QVBoxLayout(self.track_container)
        self.track_layout.setContentsMargins(0, 0, 0, 0)
        self.track_layout.setSpacing(2)
        
        scroll_area.setWidget(self.track_container)
        layout.addWidget(scroll_area)
        
        # Apply styles
        self.applyStyles(scroll_area)
    
    def createTimelineHeader(self, parent_layout):
        """Create timeline header with time markers"""
        header_frame = QFrame()
        header_frame.setFixedHeight(30)
        header_frame.setFrameStyle(QFrame.StyledPanel)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # Time markers (demo)
        time_markers = ["0:00", "0:10", "0:20", "0:30", "0:40", "0:50", "1:00"]
        for i, time in enumerate(time_markers):
            time_label = QLabel(time)
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setFixedWidth(80)
            header_layout.addWidget(time_label)
        
        header_layout.addStretch()
        parent_layout.addWidget(header_frame)
        
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: none;
            }
            QLabel {
                color: #ffffff;
                font-size: 10px;
                font-weight: bold;
            }
        """)
    
    def createDefaultTracks(self):
        """Create default tracks for different media types"""
        # Video tracks
        for i in range(1, 4):
            self.addTrack('video', f'Video {i}', '#4a90e2')
        
        # Image tracks
        for i in range(1, 3):
            self.addTrack('image', f'Image {i}', '#f39c12')
        
        # Audio tracks
        for i in range(1, 4):
            self.addTrack('audio', f'Audio {i}', '#e74c3c')
        
        # Text tracks (including captions)
        self.addTrack('text', 'Text 1', '#9b59b6')
        self.addTrack('text', 'Captions', '#2ecc71')
    
    def addTrack(self, track_type, track_name, color):
        """Add a new track to the timeline"""
        # Create track label
        track_label = QLabel(track_name)
        track_label.setFixedWidth(100)
        track_label.setFixedHeight(40)
        track_label.setAlignment(Qt.AlignCenter)
        track_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }}
        """)
        
        # Create track widget
        track = TimelineTrack(track_type, track_name, color)
        track.trackClicked.connect(self.onTrackClicked)
        
        # Create horizontal layout for label + track
        track_row = QWidget()
        track_row_layout = QHBoxLayout(track_row)
        track_row_layout.setContentsMargins(0, 0, 0, 0)
        track_row_layout.setSpacing(5)
        
        track_row_layout.addWidget(track_label)
        track_row_layout.addWidget(track, 1)  # Track takes remaining space
        
        # Add to container
        self.track_layout.addWidget(track_row)
        
        # Store track reference
        self.tracks[f"{track_type}_{track_name}"] = track
    
    def applyStyles(self, scroll_area):
        """Apply dark theme styles"""
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #2b2b2b;
                border: none;
                border-radius: 4px;
            }
            
            QScrollBar:vertical {
                background-color: #353535;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4a90e2;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #357abd;
            }
            
            QScrollBar:horizontal {
                background-color: #353535;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #4a90e2;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #357abd;
            }
        """)
    
    def addClipToTrack(self, track_type, track_name, clip_data):
        """Add a clip to a specific track"""
        track_key = f"{track_type}_{track_name}"
        if track_key in self.tracks:
            self.tracks[track_key].addClip(clip_data)
            print(f"Added clip to {track_name}: {clip_data}")
    
    def onTrackClicked(self, track_type, track_name):
        """Handle track selection"""
        selection_data = {
            'track_type': track_type,
            'track_name': track_name
        }
        self.selectionChanged.emit(track_type, selection_data)
        print(f"Timeline selection: {track_type} - {track_name}")
    
    def clearSelection(self):
        """Clear current selection"""
        self.selectionChanged.emit(None, {})
    
    # Demo methods to add sample clips
    def addSampleClips(self):
        """Add some sample clips for demonstration"""
        # Add sample video clip
        self.addClipToTrack('video', 'Video 1', {'name': 'Intro.mp4', 'duration': 10})
        
        # Add sample audio clip
        self.addClipToTrack('audio', 'Audio 1', {'name': 'BGM.mp3', 'duration': 30})
        
        # Add sample image clip
        self.addClipToTrack('image', 'Image 1', {'name': 'Logo.png', 'duration': 5})
        
        # Add sample text
        self.addClipToTrack('text', 'Text 1', {'name': 'Title', 'duration': 3})
