from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QSpinBox, 
                             QLabel, QComboBox, QSlider, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class ControlBar(QWidget):
    # Signals for various actions
    cutRequested = pyqtSignal()
    speedChanged = pyqtSignal(float)
    effectRequested = pyqtSignal()
    durationChanged = pyqtSignal(float)
    contentStyleRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_selection_type = None  # Track what's currently selected
        self.setupUI()
    
    def setupUI(self):
        """Setup control bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Cut button (enabled when something is selected)
        self.cut_btn = QPushButton("✂ Cut")
        self.cut_btn.setEnabled(False)
        self.cut_btn.clicked.connect(self.onCut)
        layout.addWidget(self.cut_btn)
        
        # Separator
        layout.addWidget(self.createSeparator())
        
        # Speed control (for audio/video)
        speed_label = QLabel("Speed:")
        layout.addWidget(speed_label)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(25)  # 0.25x
        self.speed_slider.setMaximum(400)  # 4.0x
        self.speed_slider.setValue(100)  # 1.0x
        self.speed_slider.setFixedWidth(100)
        self.speed_slider.setEnabled(False)
        self.speed_slider.valueChanged.connect(self.onSpeedChanged)
        layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setFixedWidth(40)
        layout.addWidget(self.speed_label)
        
        # Separator
        layout.addWidget(self.createSeparator())
        
        # Effect button (for text/image)
        self.effect_btn = QPushButton("✨ Effect")
        self.effect_btn.setEnabled(False)
        self.effect_btn.clicked.connect(self.onEffect)
        layout.addWidget(self.effect_btn)
        
        # Separator
        layout.addWidget(self.createSeparator())
        
        # Duration control (for image/text)
        duration_label = QLabel("Duration:")
        layout.addWidget(duration_label)
        
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(60)
        self.duration_spinbox.setValue(3)
        self.duration_spinbox.setSuffix(" sec")
        self.duration_spinbox.setEnabled(False)
        self.duration_spinbox.valueChanged.connect(self.onDurationChanged)
        layout.addWidget(self.duration_spinbox)
        
        # Separator
        layout.addWidget(self.createSeparator())
        
        # Content+Style button (for text)
        self.content_style_btn = QPushButton("📝 Content+Style")
        self.content_style_btn.setEnabled(False)
        self.content_style_btn.clicked.connect(self.onContentStyle)
        layout.addWidget(self.content_style_btn)
        
        # Add stretch to push everything to the left
        layout.addStretch()
        
        # Apply styles
        self.applyStyles()
    
    def createSeparator(self):
        """Create a vertical separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: #444444;
                background-color: #444444;
                border: none;
            }
        """)
        return separator
    
    def applyStyles(self):
        """Apply dark theme styles"""
        button_style = """
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
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
                height: 6px;
                background: #2b2b2b;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #4a90e2;
                border: none;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #357abd;
            }
            
            QSlider::sub-page:horizontal {
                background: #4a90e2;
                border-radius: 3px;
            }
        """
        
        spinbox_style = """
            QSpinBox {
                background-color: #353535;
                color: #ffffff;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                min-width: 60px;
            }
            
            QSpinBox:hover {
                border-color: #4a90e2;
            }
            
            QSpinBox:disabled {
                background-color: #2b2b2b;
                color: #888888;
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #4a90e2;
                border: none;
                width: 16px;
            }
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #357abd;
            }
        """
        
        label_style = """
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
        """
        
        # Apply styles to all components
        for btn in [self.cut_btn, self.effect_btn, self.content_style_btn]:
            btn.setStyleSheet(button_style)
        
        self.speed_slider.setStyleSheet(slider_style)
        self.duration_spinbox.setStyleSheet(spinbox_style)
        
        for label in self.findChildren(QLabel):
            label.setStyleSheet(label_style)
    
    def updateControlsForSelection(self, selection_type, selection_data=None):
        """Update control availability based on current selection"""
        self.current_selection_type = selection_type
        
        # Reset all controls
        self.cut_btn.setEnabled(False)
        self.speed_slider.setEnabled(False)
        self.effect_btn.setEnabled(False)
        self.duration_spinbox.setEnabled(False)
        self.content_style_btn.setEnabled(False)
        
        if selection_type:
            # Cut is always available when something is selected
            self.cut_btn.setEnabled(True)
            
            if selection_type in ['audio', 'video']:
                # Speed control for audio/video
                self.speed_slider.setEnabled(True)
            elif selection_type in ['text', 'image']:
                # Effect and duration for text/image
                self.effect_btn.setEnabled(True)
                self.duration_spinbox.setEnabled(True)
                
                if selection_type == 'text':
                    # Content+Style only for text
                    self.content_style_btn.setEnabled(True)
    
    # Event handlers
    def onCut(self):
        """Handle cut action"""
        print(f"Cut requested for {self.current_selection_type}")
        self.cutRequested.emit()
    
    def onSpeedChanged(self, value):
        """Handle speed change"""
        speed = value / 100.0  # Convert to decimal
        self.speed_label.setText(f"{speed:.1f}x")
        print(f"Speed changed to {speed}x")
        self.speedChanged.emit(speed)
    
    def onEffect(self):
        """Handle effect request"""
        print(f"Effect requested for {self.current_selection_type}")
        self.effectRequested.emit()
    
    def onDurationChanged(self, value):
        """Handle duration change"""
        print(f"Duration changed to {value} seconds")
        self.durationChanged.emit(float(value))
    
    def onContentStyle(self):
        """Handle content+style request"""
        print("Content+Style requested for text")
        self.contentStyleRequested.emit()
