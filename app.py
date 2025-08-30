import gradio as gr
import os
import sys
from typing import List, Dict, Any, Tuple, Optional
import json
import tempfile
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import audio processing functions directly
import uuid
from pydub import AudioSegment
from pydub.silence import split_on_silence
import re 

def clean_file_name(file_path):
    # Get the base file name and extension
    file_name = os.path.basename(file_path)
    file_name, file_extension = os.path.splitext(file_name)

    # Replace non-alphanumeric characters with an underscore
    cleaned = re.sub(r'[^a-zA-Z\d]+', '_', file_name)

    # Remove any multiple underscores
    clean_file_name = re.sub(r'_+', '_', cleaned).strip('_')

    # Generate a random UUID for uniqueness
    random_uuid = uuid.uuid4().hex[:6]

    # Combine cleaned file name with the original extension
    clean_file_path = os.path.join(os.path.dirname(file_path), clean_file_name + f"_{random_uuid}" + file_extension)

    return clean_file_path

def remove_silence(file_path, minimum_silence=50):
    sound = AudioSegment.from_file(file_path)  # auto-detects format
    audio_chunks = split_on_silence(sound,
                                    min_silence_len=100,
                                    silence_thresh=-45,
                                    keep_silence=minimum_silence) 
    combined = AudioSegment.empty()
    for chunk in audio_chunks:
        combined += chunk
    output_path = clean_file_name(file_path)        
    combined.export(output_path)  # format inferred from output file extension
    return output_path

def calculate_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_seconds = len(audio) / 1000.0  # pydub uses milliseconds
    return duration_seconds

def process_audio(audio_file, seconds=0.05):
    keep_silence = int(seconds * 1000)
    output_audio_file = remove_silence(audio_file, minimum_silence=keep_silence)
    before = calculate_duration(audio_file)
    after = calculate_duration(output_audio_file)
    text = f"Old Duration: {before:.3f} seconds \nNew Duration: {after:.3f} seconds"
    return output_audio_file, output_audio_file, text

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
        
    def process_audio_simple(self, audio_file, silence_seconds=0.05):
        """Process uploaded audio file with silence removal using working function"""
        if audio_file is None:
            return None, None, "No audio file uploaded"
        
        try:
            print(f"Processing audio: {audio_file}")
            print(f"Keep silence: {silence_seconds}s")
            
            # Use the working process_audio function
            output_file, download_file, duration_text = process_audio(audio_file, silence_seconds)
            
            self.processed_audio = output_file
            self.audio_file = audio_file
            
            print(f"Processed audio saved to: {self.processed_audio}")
            
            return self.processed_audio, download_file, duration_text
            
        except Exception as e:
            print(f"Audio processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None, f"❌ Error processing audio: {str(e)}"
    
    def add_primary_video(self, video_file):
        """Add primary video"""
        if video_file is not None:
            self.primary_video = video_file
    
    def add_secondary_video(self, video_file):
        """Add secondary video"""
        if video_file is not None:
            self.secondary_video = video_file
    
    def update_heading(self, heading_text):
        """Update heading text"""
        self.heading_text = heading_text
    
    def add_image(self, image_file, start_time, end_time):
        """Add image with timing"""
        if image_file is None or start_time >= end_time:
            return self.get_images_display()
        
        image_data = {
            'id': len(self.images_data),
            'path': image_file,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time
        }
        
        self.images_data.append(image_data)
        return self.get_images_display()
    
    def remove_image(self, image_id):
        """Remove image by ID"""
        self.images_data = [img for img in self.images_data if img['id'] != image_id]
        return self.get_images_display()
    
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
        if not text_content.strip() or start_time >= end_time:
            return self.get_texts_display()
        
        text_data = {
            'id': len(self.texts_data),
            'content': text_content,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time
        }
        
        self.texts_data.append(text_data)
        return self.get_texts_display()
    
    def remove_text(self, text_id):
        """Remove text by ID"""
        self.texts_data = [txt for txt in self.texts_data if txt['id'] != text_id]
        return self.get_texts_display()
    
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
            if not self.primary_video:
                return None, "Error: No primary video added"
            
            # Prepare video files
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
                    'position': 'center'
                })
            
            # Generate output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ultimate_short_{timestamp}.mp4"
            output_path = os.path.join("output_videos", output_filename)
            
            os.makedirs("output_videos", exist_ok=True)
            
            self.video_processor.process_video(video_files, image_overlays, output_path)
            
            return output_path, f"✅ Video saved: {output_filename}"
            
        except Exception as e:
            return None, f"❌ Error: {str(e)}"

# Initialize the editor
editor = UltimateShortEditor()

# Create the Gradio interface
def create_gradio_interface():
    with gr.Blocks(title="Ultimate Shorts Editor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎬 Ultimate Shorts Editor")
        gr.Markdown("Create amazing short videos with audio, videos, images, and text overlays!")
        
        # Row 1: Audio
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🎵 Audio")
                audio_input = gr.Audio(label="Upload Audio", type="filepath")
                
                silence_seconds = gr.Number(
                    label="Keep Silence Upto (In seconds)", 
                    value=0.05, 
                    minimum=0, 
                    maximum=1, 
                    step=0.01
                )
                audio_process_btn = gr.Button("🔧 Remove Silence", variant="primary")
                
                processed_audio_player = gr.Audio(label="Play Audio", interactive=False)
                audio_download = gr.File(label="Download Audio File")
                audio_duration = gr.Textbox(
                    label="Duration", 
                    interactive=False, 
                    lines=2
                )
        
        # Row 2: Videos
        with gr.Row():
            gr.Markdown("## 🎥 Videos")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Primary Video")
                primary_video_input = gr.Video(label="Upload Primary Video", height=250)
                primary_video_btn = gr.Button("Add Primary Video", variant="primary")
            
            with gr.Column():
                gr.Markdown("### Secondary Video")
                secondary_video_input = gr.Video(label="Upload Secondary Video", height=250)
                secondary_video_btn = gr.Button("Add Secondary Video", variant="secondary")
        
        # Row 3: Heading
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📝 Heading")
                heading_input = gr.Textbox(label="Video Heading", placeholder="Enter heading...", lines=2)
                heading_btn = gr.Button("Update Heading", variant="primary")
        
        # Row 4: Images
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🖼️ Images")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        image_input = gr.Image(label="Upload Image", type="filepath", height=200)
                    with gr.Column(scale=2):
                        with gr.Row():
                            image_start_time = gr.Number(label="Start (seconds)", value=0, minimum=0)
                            image_end_time = gr.Number(label="End (seconds)", value=5, minimum=0)
                        image_add_btn = gr.Button("➕ Add Image", variant="primary")
                
                images_display = gr.Markdown("No images added")
                
                with gr.Row():
                    image_remove_id = gr.Number(label="Remove ID", value=0, minimum=0, step=1)
                    image_remove_btn = gr.Button("🗑️ Remove", variant="stop")
        
        # Row 5: Text
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📄 Text")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        text_input = gr.Textbox(label="Text Content", placeholder="Enter text...", lines=3)
                    with gr.Column(scale=2):
                        with gr.Row():
                            text_start_time = gr.Number(label="Start (seconds)", value=0, minimum=0)
                            text_end_time = gr.Number(label="End (seconds)", value=3, minimum=0)
                        text_add_btn = gr.Button("➕ Add Text", variant="primary")
                
                texts_display = gr.Markdown("No texts added")
                
                with gr.Row():
                    text_remove_id = gr.Number(label="Remove ID", value=0, minimum=0, step=1)
                    text_remove_btn = gr.Button("🗑️ Remove", variant="stop")
        
        # Row 6: Generate Video
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🚀 Generate")
                
                generate_btn = gr.Button("🎬 Generate Final Video", variant="primary", size="lg")
                
                final_video_output = gr.Video(label="Generated Video", height=400)
                generation_status = gr.Textbox(label="Status", interactive=False)
        
        # Event handlers
        
        # Audio processing
        audio_process_btn.click(
            fn=editor.process_audio_simple,
            inputs=[audio_input, silence_seconds],
            outputs=[processed_audio_player, audio_download, audio_duration]
        )
        
        # Video handling
        primary_video_btn.click(
            fn=editor.add_primary_video,
            inputs=[primary_video_input]
        )
        
        secondary_video_btn.click(
            fn=editor.add_secondary_video,
            inputs=[secondary_video_input]
        )
        
        # Heading
        heading_btn.click(
            fn=editor.update_heading,
            inputs=[heading_input]
        )
        
        # Images
        image_add_btn.click(
            fn=editor.add_image,
            inputs=[image_input, image_start_time, image_end_time],
            outputs=[images_display]
        )
        
        image_remove_btn.click(
            fn=editor.remove_image,
            inputs=[image_remove_id],
            outputs=[images_display]
        )
        
        # Texts
        text_add_btn.click(
            fn=editor.add_text,
            inputs=[text_input, text_start_time, text_end_time],
            outputs=[texts_display]
        )
        
        text_remove_btn.click(
            fn=editor.remove_text,
            inputs=[text_remove_id],
            outputs=[texts_display]
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
