from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QFileDialog, QStackedWidget,
                             QMessageBox, QProgressBar, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap, QImage
import os
import sys
import tempfile
import time
import shutil
from vid_editor.utils import (
    add_heading, add_image_overlay, add_text_overlay,
    combine_videos, add_audio, generate_thumbnail,
    create_video_preview, get_video_info, add_captions_from_audio
)


def parse_timestamp(timestamp_str: str) -> float:
    """Parse timestamp string and return float value in seconds
    
    Args:
        timestamp_str: String like '5.5s', '1.1', 'Not specifieds', etc.
        
    Returns:
        Float value in seconds, or 0.0 if parsing fails
    """
    if not timestamp_str or timestamp_str.strip() == '':
        return 0.0
    
    # Clean the string - remove 's' suffix and whitespace
    clean_str = timestamp_str.strip().lower()
    if clean_str.endswith('s'):
        clean_str = clean_str[:-1]
    
    # Handle special cases
    if 'not specified' in clean_str or clean_str == '':
        return 0.0
    
    try:
        return float(clean_str)
    except ValueError:
        print(f"Could not parse timestamp '{timestamp_str}', using 0.0")
        return 0.0


class VideoProcessingThread(QThread):
    """Thread for processing video in the background to avoid UI freezing"""
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def run(self):
        try:
            # Extract parameters
            primary_video = self.params.get('primary_video')
            secondary_video = self.params.get('secondary_video')
            overlay_audio = self.params.get('overlay_audio')
            bg_audio = self.params.get('bg_audio')
            image_overlays = self.params.get('image_overlays', [])
            text_overlays = self.params.get('text_overlays', [])
            auto_captions = self.params.get('auto_captions', False)
            word_by_word = self.params.get('word_by_word', True)
            output_path = self.params.get('output_path')
            
            # Progress updates
            self.progress_signal.emit(10)
            
            # Combine videos if both provided
            if primary_video and os.path.exists(primary_video):
                video = combine_videos(primary_video, secondary_video)
                self.progress_signal.emit(30)
                
                # Add audio tracks if provided
                video = add_audio(video, overlay_audio, bg_audio)
                self.progress_signal.emit(50)
                
                # Process image overlays
                for image_path, timestamp in image_overlays:
                    if image_path and os.path.exists(image_path):
                        time_value = parse_timestamp(timestamp)
                        video = add_image_overlay(video, image_path, time_value)
                
                self.progress_signal.emit(70)
                
                # Process text overlays
                for text_content, timestamp in text_overlays:
                    if text_content:
                        time_value = parse_timestamp(timestamp)
                        video = add_text_overlay(video, text_content, time_value)
                
                self.progress_signal.emit(75)
                
                # Add auto-generated captions from overlay audio (if enabled and available)
                if auto_captions and overlay_audio and os.path.exists(overlay_audio):
                    caption_mode = "word-by-word" if word_by_word else "full-text"
                    print(f"🎤 Adding auto-generated captions from overlay audio ({caption_mode})...")
                    video = add_captions_from_audio(video, overlay_audio, word_by_word=word_by_word)
                elif auto_captions:
                    print("⚠️  Auto-captions enabled but no overlay audio available")
                else:
                    print("ℹ️  Auto-captions disabled")
                
                self.progress_signal.emit(90)
                
                # Write the final video
                video.write_videofile(output_path, codec="h264", audio_codec="aac", threads=4, bitrate="3000k")
                video.close()
                
                # Generate a thumbnail
                thumbnail_path = os.path.splitext(output_path)[0] + "_thumbnail.jpg"
                generate_thumbnail(output_path, thumbnail_path)
                
                self.progress_signal.emit(100)
                self.finished_signal.emit(output_path)
            else:
                self.error_signal.emit("Primary video file not found or not specified")
                
        except Exception as e:
            self.error_signal.emit(str(e))


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate Shorts Editor")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet(self.get_stylesheet())
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
        self.preview_path = None
        self.initUI()

    def get_stylesheet(self):
        return """
        /* Main Application Background */
        QWidget {
            background-color: #0d0d0d;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            font-size: 12px;
        }
        
        /* Title Labels */
        QLabel {
            color: #ffffff;
            font-size: 12px;
            font-weight: 500;
            margin: 0px;
            padding: 0px;
            background: transparent;
            border: none;
        }
        
        /* Input Fields */
        QLineEdit {
            background-color: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
            color: #ffffff;
            font-weight: 400;
            selection-background-color: #007aff;
            selection-color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #007aff;
            background-color: #1a1a1a;
            outline: none;
        }
        
        QLineEdit:hover {
            border: 1px solid #3a3a3a;
        }
        
        /* Primary Buttons */
        QPushButton {
            background-color: #404040;
            border: none;
            border-radius: 4px;
            color: #ffffff;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 500;
            min-height: 10px;
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
        
        /* Browse Buttons */
        QPushButton#browse_btn {
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 500;
            min-width: 45px;
        }
        
        QPushButton#browse_btn:hover {
            background-color: #3a3a3a;
            border: 1px solid #4a4a4a;
        }
        
        QPushButton#browse_btn:pressed {
            background-color: #1a1a1a;
        }
        
        /* Add Button */
        QPushButton#add_btn {
            background-color: #404040;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 600;
            min-width: 60px;
        }
        
        QPushButton#add_btn:hover {
            background-color: #505050;
        }
        
        QPushButton#add_btn:pressed {
            background-color: #353535;
        }
        
        /* Remove Button */
        QPushButton#remove_btn {
            background-color: #555555;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 600;
            min-width: 60px;
        }
        
        QPushButton#remove_btn:hover {
            background-color: #656565;
        }
        
        QPushButton#remove_btn:pressed {
            background-color: #454545;
        }
        
        /* Submit Button */
        QPushButton#submit_btn {
            background-color: #404040;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 600;
            margin: 8px 0;
        }
        
        QPushButton#submit_btn:hover {
            background-color: #505050;
        }
        
        QPushButton#submit_btn:pressed {
            background-color: #353535;
        }
        
        /* Section Frames */
        QFrame {
            background-color: #1a1a1a;
            border: none;
            border-radius: 6px;
            margin: 4px 0;
            padding: 8px;
        }
        
        QFrame#image_frame {
            background-color: #1a1a1a;
            border: none;
            border-radius: 4px;
            margin: 2px 0;
            padding: 6px;
        }
        
        /* Scroll Area */
        QScrollArea {
            border: none;
            background-color: #0d0d0d;
        }
        
        QScrollArea > QWidget > QWidget {
            background-color: #0d0d0d;
        }
        
        /* Scroll Bar */
        QScrollBar:vertical {
            background-color: transparent;
            width: 4px;
            border-radius: 2px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3a3a3a;
            border-radius: 2px;
            min-height: 15px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4a4a4a;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        /* Progress Bar */
        QProgressBar {
            background-color: #1a1a1a;
            border: none;
            border-radius: 3px;
            height: 6px;
            margin: 0px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #007aff;
            border-radius: 3px;
        }
        """

    def initUI(self):
        # Create stacked widget for page navigation
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.page1 = self.create_input_page()
        self.page2 = self.create_preview_page()
        
        # Add pages to stack
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        
        # Initialize UI state
        self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Clean up temporary files from previous sessions"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        else:
            # Clean up old files
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    def create_input_page(self):
        # Create main scroll area for page 1
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Main widget inside scroll area
        scroll_widget = QWidget()
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Page title
        title = QLabel("Media Input")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            margin: 20px 0;
            background: none;
            border: none;
        """)
        main_layout.addWidget(title)
        
        # Video inputs section
        video_frame = QFrame()
        video_layout = QVBoxLayout(video_frame)
        video_layout.setSpacing(8)
        
        video_title = QLabel("Video Files")
        video_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 8px;")
        video_layout.addWidget(video_title)
        
        # Video 1
        video1_layout = QHBoxLayout()
        video1_layout.setSpacing(8)
        self.label_video1 = QLabel("Primary:")
        self.label_video1.setFixedWidth(80)
        video1_layout.addWidget(self.label_video1)
        self.input_video1 = QLineEdit()
        self.input_video1.setPlaceholderText("Select main video...")
        self.input_video1.textChanged.connect(self.clear_preview)
        video1_layout.addWidget(self.input_video1)
        self.browse_video1_btn = QPushButton("Browse")
        self.browse_video1_btn.setObjectName("browse_btn")
        self.browse_video1_btn.clicked.connect(lambda: self.browse_file(self.input_video1, "Video Files (*.mp4 *.avi *.mov *.mkv)"))
        video1_layout.addWidget(self.browse_video1_btn)
        video_layout.addLayout(video1_layout)
        
        # Video 2
        video2_layout = QHBoxLayout()
        video2_layout.setSpacing(8)
        self.label_video2 = QLabel("Secondary:")
        self.label_video2.setFixedWidth(80)
        video2_layout.addWidget(self.label_video2)
        self.input_video2 = QLineEdit()
        self.input_video2.setPlaceholderText("Select secondary video...")
        self.input_video2.textChanged.connect(self.clear_preview)
        video2_layout.addWidget(self.input_video2)
        self.browse_video2_btn = QPushButton("Browse")
        self.browse_video2_btn.setObjectName("browse_btn")
        self.browse_video2_btn.clicked.connect(lambda: self.browse_file(self.input_video2, "Video Files (*.mp4 *.avi *.mov *.mkv)"))
        video2_layout.addWidget(self.browse_video2_btn)
        video_layout.addLayout(video2_layout)
        
        main_layout.addWidget(video_frame)
        
        # Audio input section
        audio_frame = QFrame()
        audio_layout = QVBoxLayout(audio_frame)
        audio_layout.setSpacing(8)
        
        audio_title = QLabel("Audio Files")
        audio_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 8px;")
        audio_layout.addWidget(audio_title)
        
        # Overlay Audio
        overlay_audio_layout = QHBoxLayout()
        overlay_audio_layout.setSpacing(8)
        self.label_overlay_audio = QLabel("Overlay:")
        self.label_overlay_audio.setFixedWidth(80)
        overlay_audio_layout.addWidget(self.label_overlay_audio)
        self.input_overlay_audio = QLineEdit()
        self.input_overlay_audio.setPlaceholderText("Select overlay audio...")
        overlay_audio_layout.addWidget(self.input_overlay_audio)
        self.browse_overlay_audio_btn = QPushButton("Browse")
        self.browse_overlay_audio_btn.setObjectName("browse_btn")
        self.browse_overlay_audio_btn.clicked.connect(lambda: self.browse_file(self.input_overlay_audio, "Audio Files (*.mp3 *.wav *.aac *.flac)"))
        overlay_audio_layout.addWidget(self.browse_overlay_audio_btn)
        audio_layout.addLayout(overlay_audio_layout)
        
        # Background Audio
        bg_audio_layout = QHBoxLayout()
        bg_audio_layout.setSpacing(8)
        self.label_bg_audio = QLabel("Background:")
        self.label_bg_audio.setFixedWidth(80)
        bg_audio_layout.addWidget(self.label_bg_audio)
        self.input_bg_audio = QLineEdit()
        self.input_bg_audio.setPlaceholderText("Select background audio...")
        bg_audio_layout.addWidget(self.input_bg_audio)
        self.browse_bg_audio_btn = QPushButton("Browse")
        self.browse_bg_audio_btn.setObjectName("browse_btn")
        self.browse_bg_audio_btn.clicked.connect(lambda: self.browse_file(self.input_bg_audio, "Audio Files (*.mp3 *.wav *.aac *.flac)"))
        bg_audio_layout.addWidget(self.browse_bg_audio_btn)
        audio_layout.addLayout(bg_audio_layout)
        
        # Auto-generate captions checkbox
        caption_layout = QHBoxLayout()
        caption_layout.setSpacing(8)
        # Import QCheckBox
        from PyQt5.QtWidgets import QCheckBox
        self.auto_captions_checkbox = QCheckBox("Auto-generate captions from overlay audio")
        self.auto_captions_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 12px;
                font-weight: 500;
                margin: 4px 0;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #007aff;
                border: 1px solid #007aff;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #0056cc;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #4a4a4a;
            }
        """)
        self.auto_captions_checkbox.setChecked(True)  # Default enabled
        caption_layout.addWidget(self.auto_captions_checkbox)
        caption_layout.addStretch()
        audio_layout.addLayout(caption_layout)
        
        # Word-by-word captions checkbox
        word_layout = QHBoxLayout()
        word_layout.setSpacing(8)
        self.word_by_word_checkbox = QCheckBox("Show captions one word at a time (recommended)")
        self.word_by_word_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 12px;
                font-weight: 500;
                margin: 4px 0;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #007aff;
                border: 1px solid #007aff;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #0056cc;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #4a4a4a;
            }
        """)
        self.word_by_word_checkbox.setChecked(True)  # Default enabled
        word_layout.addWidget(self.word_by_word_checkbox)
        word_layout.addStretch()
        audio_layout.addLayout(word_layout)
        
        main_layout.addWidget(audio_frame)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        self.next_btn = QPushButton("Next: Preview & Overlays")
        self.next_btn.setObjectName("submit_btn")
        self.next_btn.clicked.connect(self.go_to_preview_page)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)
        
        # Set scroll area
        scroll.setWidget(scroll_widget)
        return scroll

    def create_preview_page(self):
        # Create main scroll area for page 2
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Main widget inside scroll area
        scroll_widget = QWidget()
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Page title
        title = QLabel("Preview & Overlays")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            margin: 20px 0;
            background: none;
            border: none;
        """)
        main_layout.addWidget(title)
        
        # Preview section
        preview_frame = QFrame()
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setSpacing(8)
        
        preview_title = QLabel("Video Preview")
        preview_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 8px;")
        preview_layout.addWidget(preview_title)
        
        # Preview placeholder
        self.preview_label = QLabel("Video preview will appear here")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            background-color: #2a2a2a;
            border: 2px dashed #4a4a4a;
            border-radius: 8px;
            padding: 40px;
            color: #8a8a8a;
            font-size: 14px;
            min-height: 150px;
        """)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.preview_label)
        
        # Preview actions
        preview_actions = QHBoxLayout()
        self.generate_preview_btn = QPushButton("Generate Preview")
        self.generate_preview_btn.setObjectName("browse_btn")
        self.generate_preview_btn.clicked.connect(self.generate_video_preview)
        preview_actions.addWidget(self.generate_preview_btn)
        preview_actions.addStretch()
        preview_layout.addLayout(preview_actions)
        
        # Video info
        info_layout = QHBoxLayout()
        self.video_duration_label = QLabel("Duration: --:--")
        self.video_duration_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        info_layout.addWidget(self.video_duration_label)
        info_layout.addStretch()
        self.video_resolution_label = QLabel("Resolution: --x--")
        self.video_resolution_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        info_layout.addWidget(self.video_resolution_label)
        preview_layout.addLayout(info_layout)
        
        main_layout.addWidget(preview_frame)
        
        # Images section
        images_frame = QFrame()
        images_main_layout = QVBoxLayout(images_frame)
        images_main_layout.setSpacing(8)
        
        images_header_layout = QHBoxLayout()
        images_title = QLabel("Image Overlays")
        images_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")
        images_header_layout.addWidget(images_title)
        
        images_header_layout.addStretch()
        
        self.add_image_button = QPushButton("+ Add")
        self.add_image_button.setObjectName("add_btn")
        self.add_image_button.clicked.connect(self.add_image_input)
        images_header_layout.addWidget(self.add_image_button)
        
        self.remove_image_button = QPushButton("- Remove")
        self.remove_image_button.setObjectName("remove_btn")
        self.remove_image_button.clicked.connect(self.remove_last_image_input)
        images_header_layout.addWidget(self.remove_image_button)
        
        images_main_layout.addLayout(images_header_layout)
        
        self.images_layout = QVBoxLayout()
        self.images_layout.setSpacing(6)
        self.images = []
        images_main_layout.addLayout(self.images_layout)
        
        main_layout.addWidget(images_frame)
        
        # Text overlays section
        text_frame = QFrame()
        text_main_layout = QVBoxLayout(text_frame)
        text_main_layout.setSpacing(8)
        
        text_header_layout = QHBoxLayout()
        text_title = QLabel("Text Overlays")
        text_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")
        text_header_layout.addWidget(text_title)
        
        text_header_layout.addStretch()
        
        self.add_text_button = QPushButton("+ Add")
        self.add_text_button.setObjectName("add_btn")
        self.add_text_button.clicked.connect(self.add_text_input)
        text_header_layout.addWidget(self.add_text_button)
        
        self.remove_text_button = QPushButton("- Remove")
        self.remove_text_button.setObjectName("remove_btn")
        self.remove_text_button.clicked.connect(self.remove_last_text_input)
        text_header_layout.addWidget(self.remove_text_button)
        
        text_main_layout.addLayout(text_header_layout)
        
        self.texts_layout = QVBoxLayout()
        self.texts_layout.setSpacing(6)
        self.texts = []
        text_main_layout.addLayout(self.texts_layout)
        
        main_layout.addWidget(text_frame)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Media")
        self.back_btn.setObjectName("browse_btn")
        self.back_btn.clicked.connect(self.go_to_input_page)
        nav_layout.addWidget(self.back_btn)
        
        nav_layout.addStretch()
        
        self.finish_btn = QPushButton("Finish & Save Video")
        self.finish_btn.setObjectName("submit_btn")
        self.finish_btn.clicked.connect(self.finish_video)
        nav_layout.addWidget(self.finish_btn)
        
        main_layout.addLayout(nav_layout)
        
        # Set scroll area
        scroll.setWidget(scroll_widget)
        return scroll

    def go_to_preview_page(self):
        primary_video = self.input_video1.text()
        if not primary_video or not os.path.exists(primary_video):
            QMessageBox.warning(self, "Missing Video", "Please select a primary video file")
            return
            
        # Update preview info when switching to page 2
        self.update_preview_info()
        self.stacked_widget.setCurrentIndex(1)
    
    def go_to_input_page(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def clear_preview(self):
        """Clear the video preview when inputs change"""
        self.preview_label.setText("Video preview will appear here")
        self.preview_label.setStyleSheet("""
            background-color: #2a2a2a;
            border: 2px dashed #4a4a4a;
            border-radius: 8px;
            padding: 40px;
            color: #8a8a8a;
            font-size: 14px;
            min-height: 150px;
        """)
        
        # Clean up the preview file if it exists
        if self.preview_path and os.path.exists(self.preview_path):
            try:
                os.unlink(self.preview_path)
                self.preview_path = None
            except Exception as e:
                print(f"Error cleaning up preview: {e}")

    def generate_video_preview(self):
        """Generate a preview of the video"""
        primary_video = self.input_video1.text()
        if not primary_video or not os.path.exists(primary_video):
            QMessageBox.warning(self, "Missing Video", "Please select a primary video file")
            return
            
        # Show a temporary message
        self.preview_label.setText("Generating preview...")
        
        try:
            # Generate a unique preview file path
            preview_filename = f"preview_{int(time.time())}.mp4"
            self.preview_path = os.path.join(self.temp_dir, preview_filename)
            
            # Generate the preview
            preview_path = create_video_preview(primary_video, self.preview_path, duration=5)
            
            if preview_path and os.path.exists(preview_path):
                # Take a screenshot of the first frame for display
                thumbnail_path = os.path.splitext(self.preview_path)[0] + ".jpg"
                generate_thumbnail(self.preview_path, thumbnail_path)
                
                if os.path.exists(thumbnail_path):
                    # Display the thumbnail
                    pixmap = QPixmap(thumbnail_path)
                    scaled_pixmap = pixmap.scaled(640, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
                    
                    # Update the style to remove the border
                    self.preview_label.setStyleSheet("""
                        background-color: transparent;
                        border: none;
                        padding: 0px;
                    """)
            else:
                self.preview_label.setText("Failed to generate preview")
                
        except Exception as e:
            self.preview_label.setText(f"Error: {str(e)}")
    
    def update_preview_info(self):
        # Update preview label with media info
        primary_video = self.input_video1.text()
        if primary_video and os.path.exists(primary_video):
            # Get actual video info
            info = get_video_info(primary_video)
            if info:
                mins = int(info['duration'] // 60)
                secs = int(info['duration'] % 60)
                self.video_duration_label.setText(f"Duration: {mins:02d}:{secs:02d}")
                self.video_resolution_label.setText(f"Resolution: {info['width']}x{info['height']}")
            else:
                self.preview_label.setText(f"Video: {os.path.basename(primary_video)}")
                self.video_duration_label.setText("Duration: --:--")
                self.video_resolution_label.setText("Resolution: --x--")
        else:
            self.preview_label.setText("No primary video selected")
            self.video_duration_label.setText("Duration: --:--")
            self.video_resolution_label.setText("Resolution: --x--")

    def browse_file(self, line_edit, file_filter):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if file_path:
            line_edit.setText(file_path)

    def add_image_input(self):
        image_frame = QFrame()
        image_frame.setObjectName("image_frame")
        
        h_layout = QVBoxLayout(image_frame)
        h_layout.setSpacing(6)
        
        # Image path row
        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)
        path_label = QLabel(f"Image {len(self.images) + 1}:")
        path_label.setStyleSheet("font-size: 12px; margin: 0;")
        path_label.setFixedWidth(70)
        path_layout.addWidget(path_label)
        
        image_path_input = QLineEdit()
        image_path_input.setPlaceholderText("Select image...")
        path_layout.addWidget(image_path_input)
        
        browse_img_btn = QPushButton("Browse")
        browse_img_btn.setObjectName("browse_btn")
        browse_img_btn.clicked.connect(lambda: self.browse_file(image_path_input, "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"))
        path_layout.addWidget(browse_img_btn)
        
        h_layout.addLayout(path_layout)
        
        # Timestamp row
        timestamp_layout = QHBoxLayout()
        timestamp_layout.setSpacing(8)
        timestamp_label = QLabel("Time (s):")
        timestamp_label.setStyleSheet("font-size: 12px; margin: 0;")
        timestamp_label.setFixedWidth(70)
        timestamp_layout.addWidget(timestamp_label)
        
        timestamp_input = QLineEdit()
        timestamp_input.setPlaceholderText("e.g., 5.5")
        timestamp_layout.addWidget(timestamp_input)
        timestamp_layout.addStretch()
        
        h_layout.addLayout(timestamp_layout)
        
        self.images_layout.addWidget(image_frame)
        self.images.append((image_path_input, timestamp_input, image_frame))

    def remove_last_image_input(self):
        if self.images:
            _, _, image_frame = self.images.pop()
            image_frame.deleteLater()

    def add_text_input(self):
        text_frame = QFrame()
        text_frame.setObjectName("image_frame")
        
        h_layout = QVBoxLayout(text_frame)
        h_layout.setSpacing(6)
        
        # Text content row
        text_layout = QHBoxLayout()
        text_layout.setSpacing(8)
        text_label = QLabel(f"Text {len(self.texts) + 1}:")
        text_label.setStyleSheet("font-size: 12px; margin: 0;")
        text_label.setFixedWidth(70)
        text_layout.addWidget(text_label)
        
        text_input = QLineEdit()
        text_input.setPlaceholderText("Enter text to overlay...")
        text_layout.addWidget(text_input)
        
        h_layout.addLayout(text_layout)
        
        # Timestamp row
        timestamp_layout = QHBoxLayout()
        timestamp_layout.setSpacing(8)
        timestamp_label = QLabel("Time (s):")
        timestamp_label.setStyleSheet("font-size: 12px; margin: 0;")
        timestamp_label.setFixedWidth(70)
        timestamp_layout.addWidget(timestamp_label)
        
        timestamp_input = QLineEdit()
        timestamp_input.setPlaceholderText("e.g., 5.5")
        timestamp_layout.addWidget(timestamp_input)
        timestamp_layout.addStretch()
        
        h_layout.addLayout(timestamp_layout)
        
        self.texts_layout.addWidget(text_frame)
        self.texts.append((text_input, timestamp_input, text_frame))

    def remove_last_text_input(self):
        if self.texts:
            _, _, text_frame = self.texts.pop()
            text_frame.deleteLater()

    def show_processing_dialog(self):
        """Show a processing dialog with progress bar"""
        from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel
        
        # Create a custom dialog
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("Processing Video")
        self.progress_dialog.setFixedSize(400, 100)
        self.progress_dialog.setStyleSheet("background-color: #1a1a1a;")
        
        # Create layout
        layout = QVBoxLayout(self.progress_dialog)
        
        # Add label
        label = QLabel("Processing your video... This might take a few minutes.")
        label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border: none;
                border-radius: 3px;
                height: 12px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #007aff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Make it non-modal so the main window remains accessible
        self.progress_dialog.setModal(False)
        self.progress_dialog.show()
        
        # Process events to update the UI
        QApplication.processEvents()

    def update_progress(self, value):
        """Update the progress bar value"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(value)
            QApplication.processEvents()

    def finish_video(self):
        """Process and save the final video"""
        primary_video = self.input_video1.text()
        if not primary_video or not os.path.exists(primary_video):
            QMessageBox.warning(self, "Missing Video", "Please select a primary video file")
            return
        
        # Get output file path
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
        
        output_filename = f"edited_video_{int(time.time())}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # Collect all parameters
        processing_params = {
            'primary_video': self.input_video1.text(),
            'secondary_video': self.input_video2.text() if self.input_video2.text() and os.path.exists(self.input_video2.text()) else None,
            'overlay_audio': self.input_overlay_audio.text() if self.input_overlay_audio.text() and os.path.exists(self.input_overlay_audio.text()) else None,
            'bg_audio': self.input_bg_audio.text() if self.input_bg_audio.text() and os.path.exists(self.input_bg_audio.text()) else None,
            'image_overlays': [(img.text(), ts.text()) for img, ts, _ in self.images if img.text()],
            'text_overlays': [(txt.text(), ts.text()) for txt, ts, _ in self.texts if txt.text()],
            'auto_captions': self.auto_captions_checkbox.isChecked(),
            'word_by_word': self.word_by_word_checkbox.isChecked(),
            'output_path': output_path
        }
        
        # Show processing dialog
        self.show_processing_dialog()
        
        # Create and start the processing thread
        self.processing_thread = VideoProcessingThread(processing_params)
        self.processing_thread.progress_signal.connect(self.update_progress)
        self.processing_thread.finished_signal.connect(self.on_processing_finished)
        self.processing_thread.error_signal.connect(self.on_processing_error)
        self.processing_thread.start()
        
        # Log the configuration
        print("\n" + "="*60)
        print("🎬 ULTIMATE SHORTS EDITOR - FINAL CONFIGURATION")
        print("="*60)
        print(f"📹 Primary Video: {self.input_video1.text() or 'Not specified'}")
        print(f"📹 Secondary Video: {self.input_video2.text() or 'Not specified'}")
        print(f"🎵 Overlay Audio: {self.input_overlay_audio.text() or 'Not specified'}")
        print(f"🎵 Background Audio: {self.input_bg_audio.text() or 'Not specified'}")
        print(f"🖼️ Image Overlays: {len(self.images)} images")
        
        for idx, (img_input, ts_input, _) in enumerate(self.images):
            img_path = img_input.text() or 'Not specified'
            timestamp = ts_input.text() or 'Not specified'
            print(f"   📷 Image {idx+1}: {img_path.split('/')[-1] if img_path != 'Not specified' else img_path} (at {timestamp}s)")
        
        print(f"📝 Text Overlays: {len(self.texts)} texts")
        
        for idx, (text_input, ts_input, _) in enumerate(self.texts):
            text_content = text_input.text() or 'Not specified'
            timestamp = ts_input.text() or 'Not specified'
            print(f"   💬 Text {idx+1}: '{text_content}' (at {timestamp}s)")
        
        print(f"🎤 Auto-generate Captions: {'Enabled' if self.auto_captions_checkbox.isChecked() else 'Disabled'}")
        if self.auto_captions_checkbox.isChecked():
            caption_mode = "Word-by-word" if self.word_by_word_checkbox.isChecked() else "Full-text"
            print(f"   📝 Caption Mode: {caption_mode}")
        
        print("="*60)
        print(f"✅ Video processing started! Your video will be saved to: {output_path}")
        print("="*60 + "\n")
    
    def on_processing_finished(self, output_path):
        """Handle successful video processing"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        result = QMessageBox.information(
            self,
            "Success",
            f"Video processing completed successfully!\n\nSaved to: {output_path}\n\nWould you like to open the folder?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Open the folder containing the output file
            os.system(f"open '{os.path.dirname(output_path)}'")
    
    def on_processing_error(self, error_msg):
        """Handle video processing errors"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred during video processing:\n\n{error_msg}"
        )

    def display(self):
        return self.windowTitle()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())