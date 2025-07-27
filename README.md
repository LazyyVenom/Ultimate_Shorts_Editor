# Ultimate Shorts Editor 🎬

A modern, component-based video editing application designed for creating short-form videos with advanced features like automated captions, overlays, and effects.

## ✨ Features

- **Automated Video Processing**: Combine multiple video sources seamlessly
- **Advanced Caption Generation**: AI-powered Hinglish caption generation with word-by-word timing
- **Dynamic Overlays**: Add images and text with precise timing and animations
- **Audio Integration**: Layer multiple audio tracks with automatic mixing
- **Professional Effects**: Color grading, transitions, and visual enhancements
- **Batch Processing**: Headless mode for automated video generation
- **Modern Architecture**: Clean, component-based design for easy maintenance and extension
- **Custom Fonts**: Use custom font files for professional styling

### User Interface

- **Intuitive PyQt5 GUI**: Easy-to-use interface with drag-and-drop support
- **Real-time Preview**: Preview your edits before final rendering

## 🏗️ Architecture Overview

The project has been completely reorganized into a modern, component-based architecture:

```
src/
├── models/          # Data models and entities
├── services/        # Business logic services
├── processors/      # Specialized processing modules
├── ui/             # User interface components
└── app.py          # Main application orchestrator
```

**Key Benefits:**

- **Separation of Concerns**: Clear boundaries between data, business logic, and UI
- **Reusability**: Components can be used independently or in different combinations
- **Testability**: Each component can be unit tested in isolation
- **Maintainability**: Easy to understand, modify, and extend
- **Type Safety**: Full type annotations for better IDE support and error catching

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- PyQt5
- MoviePy 2.x
- FFmpeg

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/LazyyVenom/Ultimate_Shorts_Editor.git
   cd Ultimate_Shorts_Editor
   ```

2. **Create and activate virtual environment**:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage Options

#### 1. GUI Mode (Recommended)

```bash
# New organized application
python app_organized.py

# Load existing project
python app_organized.py --config my_project.use_project
```

#### 2. Headless Mode (Batch Processing)

```bash
python app_organized.py --headless --config project.use_project --output final_video.mp4
```

#### 3. Legacy Interface

```bash
# Original interface (still supported)
python app.py
```

#### 4. Try the Demo

```bash
# Explore the new architecture
python demo_organized.py
```

## 🎯 New Usage Examples

### Simple Video Creation

```python
from src.app import UltimateShortEditorApplication

# Create application
app = UltimateShortEditorApplication()

# Create project
project = app.create_project("My Awesome Video")

# Add media files
app.add_media("input_video.mp4")
app.add_media("background_music.mp3")

# Add overlays
app.add_text_overlay("Welcome!", start_time=0, duration=3)
app.add_image_overlay("logo.png", start_time=5, duration=2)

# Export video
output_path = app.export_video()
print(f"Video created: {output_path}")
```

## 📂 Legacy vs New Structure

| Aspect                | Legacy               | New Organized                |
| --------------------- | -------------------- | ---------------------------- |
| **Entry Point**       | `app.py`             | `app_organized.py`           |
| **Architecture**      | Procedural functions | Component-based OOP          |
| **Code Organization** | Scattered in utils   | Organized in services/models |
| **Testing**           | Difficult to test    | Easily testable components   |
| **Reusability**       | Limited              | High reusability             |
| **Type Safety**       | Minimal              | Full type annotations        |
| **Error Handling**    | Basic                | Comprehensive validation     |
| **Extensibility**     | Hard to extend       | Easy to add features         |

## 📖 Documentation

- **[Architecture Documentation](ARCHITECTURE.md)**: Detailed explanation of the new architecture
- **Migration Guide**: How to migrate from legacy code
- **Contributing Guidelines**: How to contribute to the project

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the new architecture patterns
4. Add tests for new functionality
5. Ensure code follows style guidelines
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MoviePy**: Video processing library
- **Faster-Whisper**: Speech recognition for captions
- **PyQt5**: GUI framework
- **FFmpeg**: Multimedia processing

---

_Built with ❤️ for content creators who want professional results with minimal effort._
