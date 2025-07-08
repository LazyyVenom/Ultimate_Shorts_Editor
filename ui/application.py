from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QFileDialog, QStackedWidget)
from PyQt5.QtCore import Qt
import sys


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate Shorts Editor")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet(self.get_stylesheet())
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
            border: 1px solid #2a2a2a;
            border-radius: 6px;
            margin: 4px 0;
            padding: 8px;
        }
        
        QFrame#image_frame {
            background-color: #1a1a1a;
            border: 1px solid #2a2a2a;
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
        self.input_bg_audio.setText("/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/overlay_audio.wav")
        bg_audio_layout.addWidget(self.input_bg_audio)
        self.browse_bg_audio_btn = QPushButton("Browse")
        self.browse_bg_audio_btn.setObjectName("browse_btn")
        self.browse_bg_audio_btn.clicked.connect(lambda: self.browse_file(self.input_bg_audio, "Audio Files (*.mp3 *.wav *.aac *.flac)"))
        bg_audio_layout.addWidget(self.browse_bg_audio_btn)
        audio_layout.addLayout(bg_audio_layout)
        
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
        preview_layout.addWidget(self.preview_label)
        
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
        # Update preview info when switching to page 2
        self.update_preview_info()
        self.stacked_widget.setCurrentIndex(1)
    
    def go_to_input_page(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def update_preview_info(self):
        # Update preview label with media info
        primary_video = self.input_video1.text()
        if primary_video:
            self.preview_label.setText(f"Primary: {primary_video.split('/')[-1]}")
            # You can add actual video duration/resolution detection here
            self.video_duration_label.setText("Duration: 0:30")  # Placeholder
            self.video_resolution_label.setText("Resolution: 1920x1080")  # Placeholder
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

    def finish_video(self):
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
        
        print("="*60)
        print("✅ Video processing started! Your short video will be saved shortly.")
        print("="*60 + "\n")

    def display(self):
        return self.windowTitle()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())