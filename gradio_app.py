import gradio as gr
import os
import sys
from typing import List, Dict, Any, Tuple, Optional
import json
import tempfile
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.utilities.video_processor import VideoProcessor
except ImportError:
    print("Warning: VideoProcessor not available. Creating mock class.")
    class VideoProcessor:
        def process_video(self, *args, **kwargs):
            return "Mock processing - VideoProcessor not available"
        def get_video_info(self, path):
            return {"duration": 10.0, "fps": 30, "size": (1920, 1080), "filename": os.path.basename(path)}

class UltimateShortEditor:
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.audio_file = None
        self.primary_video = None
        self.secondary_video = None
        self.heading_text = ""
        self.images_data = []
        self.texts_data = []
        self.processed_audio = None
        
    def process_audio(self, audio_file):
        """Process uploaded audio file"""
        if audio_file is None:
            return None, "No audio file uploaded"
        
        self.audio_file = audio_file
        # In a real implementation, you would process the audio here
        # For now, we'll just return the same file
        self.processed_audio = audio_file
        return audio_file, f"Audio processed: {os.path.basename(audio_file)}"
    
    def add_primary_video(self, video_file):
        """Add primary video"""
        if video_file is None:
            return "No video file uploaded"
        
        self.primary_video = video_file
        info = self.video_processor.get_video_info(video_file)
        return f"Primary video added: {info.get('filename', 'Unknown')} - Duration: {info.get('duration', 0):.2f}s"
    
    def add_secondary_video(self, video_file):
        """Add secondary video"""
        if video_file is None:
            return "No video file uploaded"
        
        self.secondary_video = video_file
        info = self.video_processor.get_video_info(video_file)
        return f"Secondary video added: {info.get('filename', 'Unknown')} - Duration: {info.get('duration', 0):.2f}s"
    
    def update_heading(self, heading_text):
        """Update heading text"""
        self.heading_text = heading_text
        return f"Heading updated: '{heading_text}'"
    
    def add_image(self, image_file, start_time, end_time):
        """Add image with timing"""
        if image_file is None:
            return self.get_images_display(), "No image file uploaded"
        
        if start_time >= end_time:
            return self.get_images_display(), "Start time must be less than end time"
        
        image_data = {
            'id': len(self.images_data),
            'path': image_file,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time
        }
        
        self.images_data.append(image_data)
        return self.get_images_display(), f"Image added: {os.path.basename(image_file)} ({start_time}s - {end_time}s)"
    
    def remove_image(self, image_id):
        """Remove image by ID"""
        self.images_data = [img for img in self.images_data if img['id'] != image_id]
        return self.get_images_display(), f"Image {image_id} removed"
    
    def get_images_display(self):
        """Get formatted display of all images"""
        if not self.images_data:
            return "No images added yet"
        
        display_text = "**Added Images:**\n\n"
        for img in self.images_data:
            display_text += f"• **ID {img['id']}**: {os.path.basename(img['path'])} ({img['start_time']}s - {img['end_time']}s)\n"
        
        return display_text
    
    def add_text(self, text_content, start_time, end_time):
        """Add text with timing"""
        if not text_content.strip():
            return self.get_texts_display(), "Text content cannot be empty"
        
        if start_time >= end_time:
            return self.get_texts_display(), "Start time must be less than end time"
        
        text_data = {
            'id': len(self.texts_data),
            'content': text_content,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time
        }
        
        self.texts_data.append(text_data)
        return self.get_texts_display(), f"Text added: '{text_content[:30]}...' ({start_time}s - {end_time}s)"
    
    def remove_text(self, text_id):
        """Remove text by ID"""
        self.texts_data = [txt for txt in self.texts_data if txt['id'] != text_id]
        return self.get_texts_display(), f"Text {text_id} removed"
    
    def get_texts_display(self):
        """Get formatted display of all texts"""
        if not self.texts_data:
            return "No texts added yet"
        
        display_text = "**Added Texts:**\n\n"
        for txt in self.texts_data:
            display_text += f"• **ID {txt['id']}**: '{txt['content'][:50]}...' ({txt['start_time']}s - {txt['end_time']}s)\n"
        
        return display_text
    
    def generate_final_video(self):
        """Generate the final video with all components"""
        try:
            # Validate inputs
            if not self.primary_video:
                return None, "Error: No primary video added"
            
            # Prepare video files list
            video_files = [self.primary_video]
            if self.secondary_video:
                video_files.append(self.secondary_video)
            
            # Prepare image overlays
            image_overlays = []
            for img_data in self.images_data:
                image_overlays.append({
                    'image_path': img_data['path'],
                    'start_time': img_data['start_time'],
                    'duration': img_data['duration'],
                    'position': 'center'  # Default position
                })
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ultimate_short_{timestamp}.mp4"
            output_path = os.path.join("output_videos", output_filename)
            
            # Create output directory if it doesn't exist
            os.makedirs("output_videos", exist_ok=True)
            
            # Process video
            self.video_processor.process_video(video_files, image_overlays, output_path)
            
            return output_path, f"Video generated successfully: {output_filename}"
            
        except Exception as e:
            return None, f"Error generating video: {str(e)}"

# Initialize the editor
editor = UltimateShortEditor()

# Create the Gradio interface
def create_gradio_interface():
    with gr.Blocks(title="Ultimate Shorts Editor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎬 Ultimate Shorts Editor")
        gr.Markdown("Create amazing short videos with audio, videos, images, and text overlays!")
        
        # Row 1: Add Audio
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🎵 Row 1: Audio Processing")
                with gr.Row():
                    audio_input = gr.Audio(
                        label="Upload Audio File",
                        type="filepath",
                        show_download_button=True
                    )
                    audio_process_btn = gr.Button("Process Audio", variant="primary")
                
                with gr.Row():
                    processed_audio_player = gr.Audio(
                        label="Processed Audio (Playable with Timeline)",
                        interactive=False,
                        show_download_button=True
                    )
                
                audio_status = gr.Textbox(
                    label="Audio Status",
                    interactive=False,
                    placeholder="Upload and process audio to see status here"
                )
        
        # Row 2: Add Videos (Two Columns)
        with gr.Row():
            gr.Markdown("## 🎥 Row 2: Video Files")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Primary Video")
                primary_video_input = gr.Video(
                    label="Upload Primary Video",
                    height=300
                )
                primary_video_btn = gr.Button("Add Primary Video", variant="primary")
                primary_video_status = gr.Textbox(
                    label="Primary Video Status",
                    interactive=False,
                    placeholder="Upload primary video to see info here"
                )
            
            with gr.Column():
                gr.Markdown("### Secondary Video")
                secondary_video_input = gr.Video(
                    label="Upload Secondary Video",
                    height=300
                )
                secondary_video_btn = gr.Button("Add Secondary Video", variant="secondary")
                secondary_video_status = gr.Textbox(
                    label="Secondary Video Status",
                    interactive=False,
                    placeholder="Upload secondary video to see info here"
                )
        
        # Row 3: Add Heading
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📝 Row 3: Heading")
                heading_input = gr.Textbox(
                    label="Video Heading",
                    placeholder="Enter your video heading here...",
                    lines=2
                )
                heading_btn = gr.Button("Update Heading", variant="primary")
                heading_status = gr.Textbox(
                    label="Heading Status",
                    interactive=False,
                    placeholder="Enter heading to see status here"
                )
        
        # Row 4: Add Images with scrollable interface
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🖼️ Row 4: Image Overlays")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        image_input = gr.Image(
                            label="Upload Image",
                            type="filepath",
                            height=200
                        )
                    with gr.Column(scale=2):
                        with gr.Row():
                            image_start_time = gr.Number(
                                label="Start Time (seconds)",
                                value=0,
                                minimum=0
                            )
                            image_end_time = gr.Number(
                                label="End Time (seconds)",
                                value=5,
                                minimum=0
                            )
                        image_add_btn = gr.Button("➕ Add Image", variant="primary")
                
                with gr.Row():
                    images_display = gr.Markdown(
                        "No images added yet",
                        label="Added Images"
                    )
                
                with gr.Row():
                    image_remove_id = gr.Number(
                        label="Remove Image ID",
                        value=0,
                        minimum=0,
                        step=1
                    )
                    image_remove_btn = gr.Button("🗑️ Remove Image", variant="stop")
                
                image_status = gr.Textbox(
                    label="Image Status",
                    interactive=False,
                    placeholder="Add images to see status here"
                )
        
        # Row 5: Add Text with similar interface to images
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📄 Row 5: Text Overlays")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        text_input = gr.Textbox(
                            label="Text Content",
                            placeholder="Enter text to overlay on video...",
                            lines=3
                        )
                    with gr.Column(scale=2):
                        with gr.Row():
                            text_start_time = gr.Number(
                                label="Start Time (seconds)",
                                value=0,
                                minimum=0
                            )
                            text_end_time = gr.Number(
                                label="End Time (seconds)",
                                value=3,
                                minimum=0
                            )
                        text_add_btn = gr.Button("➕ Add Text", variant="primary")
                
                with gr.Row():
                    texts_display = gr.Markdown(
                        "No texts added yet",
                        label="Added Texts"
                    )
                
                with gr.Row():
                    text_remove_id = gr.Number(
                        label="Remove Text ID",
                        value=0,
                        minimum=0,
                        step=1
                    )
                    text_remove_btn = gr.Button("🗑️ Remove Text", variant="stop")
                
                text_status = gr.Textbox(
                    label="Text Status",
                    interactive=False,
                    placeholder="Add texts to see status here"
                )
        
        # Row 6: Generate and Save Final Video
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🎬 Row 6: Generate Final Video")
                
                generate_btn = gr.Button(
                    "🚀 Generate and Save Final Video",
                    variant="primary",
                    size="lg"
                )
                
                with gr.Row():
                    final_video_output = gr.Video(
                        label="Generated Video",
                        height=400,
                        show_download_button=True
                    )
                
                generation_status = gr.Textbox(
                    label="Generation Status",
                    interactive=False,
                    placeholder="Click generate to create your final video"
                )
        
        # Event handlers
        
        # Audio processing
        audio_process_btn.click(
            fn=editor.process_audio,
            inputs=[audio_input],
            outputs=[processed_audio_player, audio_status]
        )
        
        # Video handling
        primary_video_btn.click(
            fn=editor.add_primary_video,
            inputs=[primary_video_input],
            outputs=[primary_video_status]
        )
        
        secondary_video_btn.click(
            fn=editor.add_secondary_video,
            inputs=[secondary_video_input],
            outputs=[secondary_video_status]
        )
        
        # Heading
        heading_btn.click(
            fn=editor.update_heading,
            inputs=[heading_input],
            outputs=[heading_status]
        )
        
        # Images
        image_add_btn.click(
            fn=editor.add_image,
            inputs=[image_input, image_start_time, image_end_time],
            outputs=[images_display, image_status]
        )
        
        image_remove_btn.click(
            fn=editor.remove_image,
            inputs=[image_remove_id],
            outputs=[images_display, image_status]
        )
        
        # Texts
        text_add_btn.click(
            fn=editor.add_text,
            inputs=[text_input, text_start_time, text_end_time],
            outputs=[texts_display, text_status]
        )
        
        text_remove_btn.click(
            fn=editor.remove_text,
            inputs=[text_remove_id],
            outputs=[texts_display, text_status]
        )
        
        # Final video generation
        generate_btn.click(
            fn=editor.generate_final_video,
            inputs=[],
            outputs=[final_video_output, generation_status]
        )
    
    return app

# Launch the application
if __name__ == "__main__":
    app = create_gradio_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
