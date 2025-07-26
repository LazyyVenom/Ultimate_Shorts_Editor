# Ultimate Shorts Editor

A powerful PyQt5-based application for automating the editing of short-form videos with advanced features including automatic caption generation.

## Features

### Core Video Editing

- **Video Combination**: Merge multiple video clips seamlessly
- **Audio Integration**: Add overlay audio and background music
- **Image Overlays**: Add images with precise timing
- **Text Overlays**: Add custom text with professional styling
- **Thumbnail Generation**: Automatic thumbnail creation

### Advanced Captioning

- **Automatic Caption Generation**: Generate captions from audio using Faster-Whisper
- **Word-by-Word Display**: Show captions one word at a time for better engagement
- **Hinglish Support**: Optimized for Hindi-English mixed content
- **Flexible Positioning**: Captions positioned at 70% height (30% from bottom)
- **Custom Fonts**: Use custom font files for professional styling

### User Interface

- **Intuitive PyQt5 GUI**: Easy-to-use interface with drag-and-drop support
- **Real-time Preview**: Preview your edits before final rendering
- **Batch Processing**: Process multiple videos efficiently
- **Progress Tracking**: Visual progress indicators for all operations

## Installation

1. Clone the repository:

```bash
git clone https://github.com/LazyyVenom/Ultimate_Shorts_Editor.git
cd Ultimate_Shorts_Editor
```

2. Create and activate virtual environment:

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

## Requirements

- Python 3.7+
- PyQt5
- MoviePy 2.x
- Faster-Whisper (for caption generation)
- FFmpeg (for video processing)

## Usage

1. **Launch the application**: Run `python app.py`
2. **Select videos**: Choose primary and secondary video files
3. **Add audio**: Upload overlay audio and background music
4. **Configure captions**: Enable auto-captions and word-by-word display
5. **Add overlays**: Insert images and text at specific timestamps
6. **Process**: Click "Process Video" to generate the final output

## Project Structure

```
Ultimate_Shorts_Editor/
├── app.py                    # Main application entry point
├── ui/
│   └── application.py        # PyQt5 user interface
├── vid_editor/
│   └── utils.py             # Core video processing utilities
├── audio_opp/
│   └── captioner.py         # Audio captioning with Faster-Whisper
├── caption_integration.py    # Caption integration utilities
├── static/
│   ├── Utendo-Bold.ttf      # Custom font files
│   └── Utendo-Regular.ttf
└── requirements.txt         # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **MoviePy**: Video processing library
- **Faster-Whisper**: Speech recognition for captions
- **PyQt5**: GUI framework
- **FFmpeg**: Multimedia processing
