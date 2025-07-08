#!/usr/bin/env python3
"""
Ultimate Shorts Editor - Main Application
A PyQt5-based application for automating the editing of short-form videos
"""

import sys
import os
import tempfile
from PyQt5.QtWidgets import QApplication
from ui.application import UI
from editor.utils import (
    add_heading, add_image_overlay, add_text_overlay,
    combine_videos, add_audio, generate_thumbnail,
    create_video_preview, get_video_info
)


def main():
    """Main function to start the Ultimate Shorts Editor application"""
    app = QApplication(sys.argv)
    
    # Create temporary directory for previews and intermediate files
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # Start the UI
    window = UI()
    window.show()
    
    # Execute the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()