"""
Main Window for Ultimate Shorts Editor
Organized UI with component-based architecture
"""

import os
import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QMenuBar, QStatusBar, QAction, QFileDialog, QMessageBox,
    QPushButton, QLabel, QProgressBar, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.video_project import VideoProject
from src.core.project_config import ProjectConfig


class ProcessingThread(QThread):
    """Background thread for video processing"""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, project: VideoProject):
        super().__init__()
        self.project = project
        
    def run(self):
        """Run video processing in background"""
        try:
            # Set up progress callback
            def progress_callback(value, message=""):
                self.progress_signal.emit(value, message)
            
            self.project.set_progress_callback('progress', progress_callback)
            
            # Process video
            output_path = self.project.process_video()
            
            if output_path:
                self.finished_signal.emit(output_path)
            else:
                self.error_signal.emit("Video processing failed - no output generated")
                
        except Exception as e:
            self.error_signal.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window with organized UI components"""
    
    def __init__(self, project: Optional[VideoProject] = None):
        super().__init__()
        
        self.project = project or VideoProject()
        self.processing_thread = None
        
        self.setWindowTitle("Ultimate Shorts Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply dark theme
        self.setStyleSheet(self.get_dark_stylesheet())
        
        # Initialize UI
        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()
        
        print("🎬 Main window initialized successfully")
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Project settings and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Preview and output
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
    
    def create_left_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Project section
        project_label = QLabel("Project Configuration")
        project_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(project_label)
        
        # Load/Save project buttons
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Project")
        load_btn.clicked.connect(self.load_project)
        button_layout.addWidget(load_btn)
        
        save_btn = QPushButton("Save Project")
        save_btn.clicked.connect(self.save_project)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Media files section
        media_label = QLabel("Media Files")
        media_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 15px 0 5px 0;")
        layout.addWidget(media_label)
        
        # Primary video
        self.primary_video_btn = QPushButton("Select Primary Video")
        self.primary_video_btn.clicked.connect(lambda: self.select_media_file('primary_video', 'Video Files (*.mp4 *.avi *.mov *.mkv)'))
        layout.addWidget(self.primary_video_btn)
        
        # Secondary video
        self.secondary_video_btn = QPushButton("Select Secondary Video (Optional)")
        self.secondary_video_btn.clicked.connect(lambda: self.select_media_file('secondary_video', 'Video Files (*.mp4 *.avi *.mov *.mkv)'))
        layout.addWidget(self.secondary_video_btn)
        
        # Overlay audio
        self.overlay_audio_btn = QPushButton("Select Overlay Audio")
        self.overlay_audio_btn.clicked.connect(lambda: self.select_media_file('overlay_audio', 'Audio Files (*.mp3 *.wav *.aac *.flac)'))
        layout.addWidget(self.overlay_audio_btn)
        
        # Background audio
        self.bg_audio_btn = QPushButton("Select Background Audio")
        self.bg_audio_btn.clicked.connect(lambda: self.select_media_file('background_audio', 'Audio Files (*.mp3 *.wav *.aac *.flac)'))
        layout.addWidget(self.bg_audio_btn)
        
        # Processing controls
        processing_label = QLabel("Processing")
        processing_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 15px 0 5px 0;")
        layout.addWidget(processing_label)
        
        # Generate preview button
        self.preview_btn = QPushButton("Generate Preview")
        self.preview_btn.clicked.connect(self.generate_preview)
        layout.addWidget(self.preview_btn)
        
        # Process video button
        self.process_btn = QPushButton("Process Full Video")
        self.process_btn.clicked.connect(self.process_video)
        layout.addWidget(self.process_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right preview panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Preview section
        preview_label = QLabel("Video Preview")
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(preview_label)
        
        # Preview placeholder
        self.preview_display = QLabel("Video preview will appear here")
        self.preview_display.setStyleSheet("""
            background-color: #2a2a2a;
            border: 2px dashed #4a4a4a;
            border-radius: 8px;
            padding: 40px;
            color: #8a8a8a;
            font-size: 14px;
            min-height: 300px;
        """)
        self.preview_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_display)
        
        # Video info section
        info_layout = QHBoxLayout()
        self.duration_label = QLabel("Duration: --:--")
        self.resolution_label = QLabel("Resolution: --x--")
        info_layout.addWidget(self.duration_label)
        info_layout.addStretch()
        info_layout.addWidget(self.resolution_label)
        layout.addLayout(info_layout)
        
        # Project info section
        project_info_label = QLabel("Project Information")
        project_info_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 15px 0 5px 0;")
        layout.addWidget(project_info_label)
        
        self.project_info_display = QLabel("No project loaded")
        self.project_info_display.setStyleSheet("""
            background-color: #1a1a1a;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 10px;
            color: #ffffff;
            font-family: monospace;
            font-size: 11px;
        """)
        self.project_info_display.setWordWrap(True)
        layout.addWidget(self.project_info_display)
        
        return panel
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Project', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open Project', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_project)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save Project', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Save Project As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        batch_action = QAction('Batch Processing', self)
        batch_action.triggered.connect(self.show_batch_processing)
        tools_menu.addAction(batch_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def select_media_file(self, file_type: str, file_filter: str):
        """Select a media file and update project configuration"""
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select {file_type}", "", file_filter)
        if file_path:
            # Update project configuration
            self.project.config.update(**{file_type: file_path})
            
            # Update button text
            filename = os.path.basename(file_path)
            if file_type == 'primary_video':
                self.primary_video_btn.setText(f"Primary: {filename}")
            elif file_type == 'secondary_video':
                self.secondary_video_btn.setText(f"Secondary: {filename}")
            elif file_type == 'overlay_audio':
                self.overlay_audio_btn.setText(f"Overlay: {filename}")
            elif file_type == 'background_audio':
                self.bg_audio_btn.setText(f"Background: {filename}")
            
            self.update_project_info()
            self.status_bar.showMessage(f"Selected {file_type}: {filename}")
    
    def update_project_info(self):
        """Update the project information display"""
        if self.project:
            info = self.project.get_project_info()
            config = info['config']
            
            info_text = f"""Project: {config['project_name']}
            
Media Files:
• Primary Video: {os.path.basename(config['primary_video']) if config['primary_video'] else 'Not selected'}
• Secondary Video: {os.path.basename(config['secondary_video']) if config['secondary_video'] else 'Not selected'}
• Overlay Audio: {os.path.basename(config['overlay_audio']) if config['overlay_audio'] else 'Not selected'}
• Background Audio: {os.path.basename(config['background_audio']) if config['background_audio'] else 'Not selected'}

Settings:
• Auto Captions: {'Yes' if config['auto_captions'] else 'No'}
• Word-by-word: {'Yes' if config['word_by_word'] else 'No'}
• Output Directory: {config['output_directory'] or 'Default'}
"""
            
            self.project_info_display.setText(info_text)
    
    def new_project(self):
        """Create a new project"""
        self.project = VideoProject()
        self.update_project_info()
        self.status_bar.showMessage("New project created")
        
        # Reset UI
        self.primary_video_btn.setText("Select Primary Video")
        self.secondary_video_btn.setText("Select Secondary Video (Optional)")
        self.overlay_audio_btn.setText("Select Overlay Audio")
        self.bg_audio_btn.setText("Select Background Audio")
        self.preview_display.setText("Video preview will appear here")
    
    def load_project(self):
        """Load a project from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Project", "", "Project Files (*.json)"
        )
        
        if file_path:
            try:
                self.project = VideoProject.load_project(file_path)
                self.update_project_info()
                self.status_bar.showMessage(f"Loaded project: {os.path.basename(file_path)}")
                
                # Update UI with loaded data
                config = self.project.config
                if config.primary_video:
                    self.primary_video_btn.setText(f"Primary: {os.path.basename(config.primary_video)}")
                if config.secondary_video:
                    self.secondary_video_btn.setText(f"Secondary: {os.path.basename(config.secondary_video)}")
                if config.overlay_audio:
                    self.overlay_audio_btn.setText(f"Overlay: {os.path.basename(config.overlay_audio)}")
                if config.background_audio:
                    self.bg_audio_btn.setText(f"Background: {os.path.basename(config.background_audio)}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
    
    def save_project(self):
        """Save the current project"""
        if hasattr(self, '_project_file_path'):
            self.project.save_project(self._project_file_path)
            self.status_bar.showMessage("Project saved")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Save the project with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "Project Files (*.json)"
        )
        
        if file_path:
            self.project.save_project(file_path)
            self._project_file_path = file_path
            self.status_bar.showMessage(f"Project saved as: {os.path.basename(file_path)}")
    
    def generate_preview(self):
        """Generate a video preview"""
        try:
            self.status_bar.showMessage("Generating preview...")
            preview_path = self.project.create_preview()
            
            if preview_path:
                # TODO: Display preview in UI
                self.preview_display.setText(f"Preview generated: {os.path.basename(preview_path)}")
                self.status_bar.showMessage("Preview generated successfully")
            else:
                self.status_bar.showMessage("Failed to generate preview")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate preview: {e}")
            self.status_bar.showMessage("Preview generation failed")
    
    def process_video(self):
        """Process the full video"""
        if not self.project.config.primary_video:
            QMessageBox.warning(self, "Missing Input", "Please select a primary video file")
            return
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
        
        self.project.config.output_directory = output_dir
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_btn.setEnabled(False)
        
        # Start processing thread
        self.processing_thread = ProcessingThread(self.project)
        self.processing_thread.progress_signal.connect(self.update_progress)
        self.processing_thread.finished_signal.connect(self.on_processing_finished)
        self.processing_thread.error_signal.connect(self.on_processing_error)
        self.processing_thread.start()
        
        self.status_bar.showMessage("Processing video...")
    
    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_bar.showMessage(f"Processing: {message} ({value}%)")
    
    def on_processing_finished(self, output_path: str):
        """Handle successful processing completion"""
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        
        QMessageBox.information(
            self, "Success",
            f"Video processing completed successfully!\n\nOutput saved to:\n{output_path}"
        )
        
        self.status_bar.showMessage(f"Processing completed: {os.path.basename(output_path)}")
    
    def on_processing_error(self, error_message: str):
        """Handle processing errors"""
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Processing Error", f"Video processing failed:\n\n{error_message}")
        self.status_bar.showMessage("Processing failed")
    
    def show_batch_processing(self):
        """Show batch processing dialog"""
        QMessageBox.information(self, "Batch Processing", "Batch processing feature coming soon!")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Ultimate Shorts Editor",
            """
            <h3>Ultimate Shorts Editor v2.0</h3>
            <p>Advanced video editing tool for creating short-form content</p>
            <p><b>Features:</b></p>
            <ul>
            <li>Video combination and editing</li>
            <li>Audio overlay and mixing</li>
            <li>Automatic caption generation</li>
            <li>Image and text overlays</li>
            <li>Visual effects and color grading</li>
            </ul>
            <p>Built with PyQt5 and MoviePy</p>
            """
        )
    
    def get_dark_stylesheet(self) -> str:
        """Get the dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #0d0d0d;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #0d0d0d;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        }
        
        QPushButton {
            background-color: #404040;
            border: none;
            border-radius: 4px;
            color: #ffffff;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #505050;
        }
        
        QPushButton:pressed {
            background-color: #353535;
        }
        
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QMenuBar {
            background-color: #1a1a1a;
            color: #ffffff;
            border-bottom: 1px solid #3a3a3a;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #404040;
        }
        
        QMenu {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #3a3a3a;
        }
        
        QMenu::item {
            padding: 6px 20px;
        }
        
        QMenu::item:selected {
            background-color: #404040;
        }
        
        QStatusBar {
            background-color: #1a1a1a;
            color: #ffffff;
            border-top: 1px solid #3a3a3a;
        }
        
        QProgressBar {
            background-color: #2a2a2a;
            border: none;
            border-radius: 3px;
            height: 20px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #007aff;
            border-radius: 3px;
        }
        
        QSplitter::handle {
            background-color: #3a3a3a;
        }
        """
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.project:
            self.project.cleanup()
        event.accept()
