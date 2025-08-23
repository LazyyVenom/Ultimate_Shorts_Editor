from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QListWidget, QPushButton, QFrame,
                             QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
    
    def setupUI(self):
        """Setup the left panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create splitter for three rows
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Create the three sections
        self.uploaded_files_section = self.createUploadedFilesSection()
        self.default_files_section = self.createDefaultFilesSection()
        self.text_captions_section = self.createTextCaptionsSection()
        
        # Add sections to splitter
        splitter.addWidget(self.uploaded_files_section)
        splitter.addWidget(self.default_files_section)
        splitter.addWidget(self.text_captions_section)
        
        # Set equal proportions
        splitter.setSizes([250, 250, 250])
    
    def createUploadedFilesSection(self):
        """Create uploaded files section"""
        section = QFrame()
        section.setFrameStyle(QFrame.NoFrame)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Uploaded Files")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Category dropdown
        category_combo = QComboBox()
        category_combo.addItems(["All", "Videos", "Audio", "Images"])
        category_combo.setFixedWidth(100)
        header_layout.addWidget(category_combo)
        
        layout.addLayout(header_layout)
        
        # File list
        file_list = QListWidget()
        file_list.setDragDropMode(QListWidget.DragOnly)
        file_list.setAlternatingRowColors(True)
        layout.addWidget(file_list)
        
        # Upload button
        upload_btn = QPushButton("Upload Files")
        upload_btn.clicked.connect(self.onUploadFiles)
        layout.addWidget(upload_btn)
        
        self.applyListStyle(file_list)
        self.applyButtonStyle(upload_btn)
        self.applyComboStyle(category_combo)
        
        return section
    
    def createDefaultFilesSection(self):
        """Create default files section"""
        section = QFrame()
        section.setFrameStyle(QFrame.NoFrame)
        section.setStyleSheet("""
            QFrame {
                border-top: 1px solid #444444;
                margin-top: 5px;
                padding-top: 5px;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Default Files")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Category dropdown
        category_combo = QComboBox()
        category_combo.addItems(["All", "Effects", "Transitions", "Music", "SFX"])
        category_combo.setFixedWidth(100)
        header_layout.addWidget(category_combo)
        
        layout.addLayout(header_layout)
        
        # File list
        file_list = QListWidget()
        file_list.setDragDropMode(QListWidget.DragOnly)
        file_list.setAlternatingRowColors(True)
        
        # Add some sample default items
        sample_items = ["Fade In Effect", "Fade Out Effect", "Zoom Effect", "Background Music 1", "Background Music 2"]
        for item in sample_items:
            file_list.addItem(item)
        
        layout.addWidget(file_list)
        
        self.applyListStyle(file_list)
        self.applyComboStyle(category_combo)
        
        return section
    
    def createTextCaptionsSection(self):
        """Create text and captions section"""
        section = QFrame()
        section.setFrameStyle(QFrame.NoFrame)
        section.setStyleSheet("""
            QFrame {
                border-top: 1px solid #444444;
                margin-top: 5px;
                padding-top: 5px;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        title_label = QLabel("Add Text and Captions")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Audio layer selection
        audio_layout = QHBoxLayout()
        audio_label = QLabel("Audio Layer:")
        audio_combo = QComboBox()
        audio_combo.addItems(["Select Audio Layer", "Audio 1", "Audio 2", "Audio 3"])
        audio_layout.addWidget(audio_label)
        audio_layout.addWidget(audio_combo)
        layout.addLayout(audio_layout)
        
        # Text input
        text_input = QTextEdit()
        text_input.setPlaceholderText("Enter text or captions here...")
        text_input.setMaximumHeight(80)
        layout.addWidget(text_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_text_btn = QPushButton("Add Text")
        add_caption_btn = QPushButton("Generate Captions")
        
        add_text_btn.clicked.connect(self.onAddText)
        add_caption_btn.clicked.connect(self.onGenerateCaptions)
        
        button_layout.addWidget(add_text_btn)
        button_layout.addWidget(add_caption_btn)
        layout.addLayout(button_layout)
        
        self.applyComboStyle(audio_combo)
        self.applyButtonStyle(add_text_btn)
        self.applyButtonStyle(add_caption_btn)
        self.applyTextEditStyle(text_input)
        
        return section
    
    def applyListStyle(self, list_widget):
        """Apply dark theme style to list widgets"""
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 5px;
                alternate-background-color: #333333;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: none;
            }
            
            QListWidget::item:selected {
                background-color: #4a90e2;
            }
            
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
    
    def applyButtonStyle(self, button):
        """Apply dark theme style to buttons"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #357abd;
            }
            
            QPushButton:pressed {
                background-color: #2968a3;
            }
        """)
    
    def applyComboStyle(self, combo):
        """Apply dark theme style to combo boxes"""
        combo.setStyleSheet("""
            QComboBox {
                background-color: #353535;
                color: #ffffff;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            
            QComboBox:hover {
                border-color: #4a90e2;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #353535;
                color: #ffffff;
                border: none;
                selection-background-color: #4a90e2;
            }
        """)
    
    def applyTextEditStyle(self, text_edit):
        """Apply dark theme style to text edit widgets"""
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            
            QTextEdit:focus {
                border-color: #4a90e2;
            }
        """)
    
    # Event handlers (placeholders for now)
    def onUploadFiles(self):
        print("Upload files clicked")
    
    def onAddText(self):
        print("Add text clicked")
    
    def onGenerateCaptions(self):
        print("Generate captions clicked")
