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

def add_image_overlay_with_animation(video, image_path: str, start_time: float, end_time: float, padding: int = 10):
    """Add image overlay with smooth up/down animation like in video_processor.py"""
    try:
        if not os.path.exists(image_path):
            print(f"Warning: Image file {image_path} not found")
            return video
            
        video_width, video_height = video.size
        
        max_width = video_width * (1 - padding / 100)
        max_height = video_height * (1 - padding / 100)
        
        image = ImageClip(image_path)
        
        img_width, img_height = image.size
        scale_width = max_width / img_width
        scale_height = max_height / img_height
        scale = min(scale_width, scale_height)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        image = image.resized((new_width, new_height))
        
        duration = end_time - start_time
        image = image.with_duration(duration).with_start(start_time)

        center_x = (video_width - new_width) // 2
        center_y = (video_height - new_height) // 2
        bottom_y = video_height

        transition_duration = min(0.5, duration / 3)

        def position_function(t):
            """Calculate position based on time with smooth animation"""
            if t < transition_duration:
                # Coming up from bottom
                progress = t / transition_duration
                progress = 1 - (1 - progress) ** 2  # Ease out
                y = bottom_y - (bottom_y - center_y) * progress
                return (center_x, y)
            elif t > (duration - transition_duration):
                # Going down to bottom
                progress = (t - (duration - transition_duration)) / transition_duration
                progress = progress ** 2  # Ease in
                y = center_y + (bottom_y - center_y) * progress
                return (center_x, y)
            else:
                # Stay in center
                return (center_x, center_y)
        
        image = image.with_position(position_function)
        
        final_video = CompositeVideoClip([video, image])
        print(f"Added animated image: {os.path.basename(image_path)}")
        
        return final_video
        
    except Exception as e:
        print(f"Error in add_image_overlay_with_animation: {e}")
        return video

try:
    from src.utilities.video_processor import (
        add_primary_secondary_videos, 
        add_image_overlay, 
        add_captions, 
        add_heading, 
        add_smaller_captions
    )
    from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
    VIDEO_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Video processing not available: {e}")
    VIDEO_PROCESSING_AVAILABLE = False
    
    # Mock functions for when video processing is not available
    def add_primary_secondary_videos(*args, **kwargs):
        return None
    def add_image_overlay(*args, **kwargs):
        return None
    def add_captions(*args, **kwargs):
        return None
    def add_heading(*args, **kwargs):
        return None
    def add_smaller_captions(*args, **kwargs):
        return None

class UltimateShortEditor:
    def __init__(self):
        self.audio_file = None
        self.primary_video = None
        self.secondary_video = None
        self.heading_text = ""
        self.images_data = []
        self.texts_data = []
        self.processed_audio = None
        self.auto_captions = None
        
    def add_bgm_to_audio(self, main_audio_clip, bgm_path=None, bgm_volume=0.15):
        """Add background music to the main audio clip"""
        if bgm_path is None:
            # Use absolute path to ensure BGM file is found
            bgm_path = os.path.join(os.path.dirname(__file__), "testing_stuff", "that-s-the-one-ryan-mccaffrey-go-by-ocean_qpn2Lcne.wav")
        
        try:
            print(f"Looking for BGM file at: {bgm_path}")
            if os.path.exists(bgm_path):
                print(f"Adding BGM from: {bgm_path}")
                bgm_clip = AudioFileClip(bgm_path)
                
                # Loop BGM to match main audio duration
                main_duration = main_audio_clip.duration
                if bgm_clip.duration < main_duration:
                    # Calculate how many loops needed
                    loops_needed = int(main_duration / bgm_clip.duration) + 1
                    bgm_clips = [bgm_clip] * loops_needed
                    
                    # Use concatenate_audioclips to loop the BGM
                    try:
                        from moviepy import concatenate_audioclips
                        bgm_clip = concatenate_audioclips(bgm_clips)
                    except ImportError:
                        try:
                            from moviepy.audio.tools.cuts import concatenate_audioclips
                            bgm_clip = concatenate_audioclips(bgm_clips)
                        except ImportError:
                            # Fallback: just use the original clip without looping
                            print("Warning: Could not loop BGM, using original length")
                            pass
                
                # Trim BGM to match main audio duration exactly
                bgm_clip = bgm_clip.subclipped(0, main_duration)
                
                # Reduce BGM volume and mix with main audio
                try:
                    # Manual volume adjustment using audio transformation
                    def adjust_volume(clip, volume_factor):
                        """Manually adjust volume by scaling audio data"""
                        return clip.transform(lambda gf, t: volume_factor * gf(t))
                    
                    bgm_clip = adjust_volume(bgm_clip, bgm_volume)
                    main_audio_clip = adjust_volume(main_audio_clip, 0.8)
                    print(f"Volume adjusted using manual scaling")
                    
                except Exception as volume_error:
                    print(f"Volume adjustment failed: {volume_error}")
                    print("Continuing with original audio volumes")
                
                # Mix the audio clips
                try:
                    # Try to import CompositeAudioClip
                    try:
                        from moviepy import CompositeAudioClip
                        mixed_audio = CompositeAudioClip([main_audio_clip, bgm_clip])
                        print(f"BGM mixed successfully using CompositeAudioClip")
                    except ImportError:
                        # Fallback: use simple addition if composite not available
                        mixed_audio = main_audio_clip + bgm_clip
                        print(f"BGM mixed using simple addition fallback")
                    
                except Exception as mix_error:
                    print(f"BGM mixing failed: {mix_error}")
                    print("Returning original audio without BGM")
                    return main_audio_clip
                
                return mixed_audio
            else:
                print(f"BGM file not found: {bgm_path}, using original audio")
                return main_audio_clip
                
        except Exception as e:
            print(f"Error adding BGM: {e}")
            return main_audio_clip
        
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
            if VIDEO_PROCESSING_AVAILABLE:
                try:
                    video_clip = VideoFileClip(video_file)
                    duration = video_clip.duration
                    size = video_clip.size
                    fps = video_clip.fps
                    video_clip.close()
                    return f"✅ Primary video loaded: {os.path.basename(video_file)}\nDuration: {duration:.1f}s, Size: {size[0]}x{size[1]}, FPS: {fps:.1f}"
                except Exception as e:
                    return f"⚠️ Video loaded but couldn't read info: {str(e)}"
            return f"✅ Primary video loaded: {os.path.basename(video_file)}"
        return "❌ No video file provided"
    
    def add_secondary_video(self, video_file):
        """Add secondary video"""
        if video_file is not None:
            self.secondary_video = video_file
            if VIDEO_PROCESSING_AVAILABLE:
                try:
                    video_clip = VideoFileClip(video_file)
                    duration = video_clip.duration
                    size = video_clip.size
                    fps = video_clip.fps
                    video_clip.close()
                    return f"✅ Secondary video loaded: {os.path.basename(video_file)}\nDuration: {duration:.1f}s, Size: {size[0]}x{size[1]}, FPS: {fps:.1f}"
                except Exception as e:
                    return f"⚠️ Video loaded but couldn't read info: {str(e)}"
            return f"✅ Secondary video loaded: {os.path.basename(video_file)}"
        return "❌ No video file provided"
    
    def update_heading(self, heading_text):
        """Update heading text"""
        self.heading_text = heading_text
        if heading_text.strip():
            return f"✅ Heading updated: '{heading_text[:50]}...'" if len(heading_text) > 50 else f"✅ Heading updated: '{heading_text}'"
        else:
            return "❌ Heading cleared"
    
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
    
    def generate_auto_captions(self):
        """Generate automatic captions and auto-generate video if ready"""
        try:
            if not self.processed_audio:
                return "❌ No processed audio available. Please process audio first.", "", None, "❌ No audio for captions"
            
            # Try to import caption processor
            try:
                from src.utilities.caption_processor import GenerateCaptions
            except ImportError:
                return "❌ Caption generation not available. Install required dependencies.", "", None, "❌ Caption generation failed"
            
            print("Generating auto captions...")
            caption_generator = GenerateCaptions(model_size="medium", device="cpu")
            caption_data = caption_generator.generate(self.processed_audio)
            
            self.auto_captions = caption_data
            
            # Create preview text
            preview_text = "Generated Captions:\n\n"
            for i, (text, start_time) in enumerate(zip(caption_data['captions'][:20], caption_data['start_times'][:20])):
                preview_text += f"{start_time:.1f}s: {text}\n"
            
            if len(caption_data['captions']) > 20:
                preview_text += f"\n... and {len(caption_data['captions']) - 20} more captions"
            
            status_text = f"✅ Generated {len(caption_data['captions'])} captions successfully!"
            
            # Auto-generate video if ready
            video_output, generation_status = self.auto_generate_if_ready()
            
            return status_text, preview_text, video_output, generation_status
            
        except Exception as e:
            print(f"Caption generation error: {e}")
            return f"❌ Error generating captions: {str(e)}", "", None, "❌ Caption generation failed"
    
    def clear_auto_captions(self):
        """Clear generated auto captions and auto-generate if ready"""
        self.auto_captions = None
        
        # Auto-generate video if ready
        video_output, generation_status = self.auto_generate_if_ready()
        
        return "✅ Auto captions cleared", "", video_output, generation_status
    
    def generate_final_video_simple(self):
        """Generate final video using the simple step-by-step method with auto captions"""
        try:
            if not VIDEO_PROCESSING_AVAILABLE:
                return None, "❌ Error: Video processing libraries not available"
            
            if not self.primary_video:
                return None, "❌ Error: No primary video uploaded"
            
            if not self.processed_audio:
                return None, "❌ Error: No processed audio available. Please process audio first."
            
            print("Starting video generation...")
            
            # Step 1: Auto-generate captions first
            print("Auto-generating captions...")
            try:
                from src.utilities.caption_processor import GenerateCaptions
                caption_generator = GenerateCaptions(model_size="medium", device="cpu")
                self.auto_captions = caption_generator.generate(self.processed_audio)
                print(f"Generated {len(self.auto_captions['captions'])} captions")
            except Exception as e:
                print(f"Caption generation failed: {e}")
                self.auto_captions = None
            
            # Load clips like in the working video_processor.py example
            primary_video = VideoFileClip(self.primary_video)
            audio_clip = AudioFileClip(self.processed_audio)
            audio_duration = audio_clip.duration
            
            print(f"Audio duration: {audio_duration:.2f} seconds")
            
            # Step 2: Combine primary and secondary videos in sequence
            if self.secondary_video:
                print("Combining primary and secondary videos in sequence...")
                secondary_video = VideoFileClip(self.secondary_video)
                
                # Calculate timing for video sequence
                primary_start_duration = 6.0  # First 6 seconds of primary video
                remaining_time = audio_duration - primary_start_duration
                secondary_duration = remaining_time * 0.45  # 40-50% of remaining time
                primary_end_duration = remaining_time - secondary_duration  # Rest for primary
                
                print(f"Video sequence: Primary({primary_start_duration}s) → Secondary({secondary_duration:.1f}s) → Primary({primary_end_duration:.1f}s)")
                
                # Create video segments
                primary_start = primary_video.subclipped(0, min(primary_start_duration, primary_video.duration))
                if primary_start.duration < primary_start_duration:
                    # Loop primary if it's shorter than 6 seconds
                    loops_needed = int(primary_start_duration / primary_video.duration) + 1
                    primary_clips = [primary_video] * loops_needed
                    try:
                        from moviepy import concatenate_videoclips
                        looped_primary = concatenate_videoclips(primary_clips)
                        primary_start = looped_primary.subclipped(0, primary_start_duration)
                    except ImportError:
                        primary_start = primary_video.subclipped(0, min(primary_start_duration, primary_video.duration))
                
                # Secondary video segment
                secondary_segment = secondary_video.subclipped(0, min(secondary_duration, secondary_video.duration))
                if secondary_segment.duration < secondary_duration:
                    # Loop secondary if needed
                    loops_needed = int(secondary_duration / secondary_video.duration) + 1
                    secondary_clips = [secondary_video] * loops_needed
                    try:
                        from moviepy import concatenate_videoclips
                        looped_secondary = concatenate_videoclips(secondary_clips)
                        secondary_segment = looped_secondary.subclipped(0, secondary_duration)
                    except ImportError:
                        secondary_segment = secondary_video.subclipped(0, min(secondary_duration, secondary_video.duration))
                
                # Primary end segment
                primary_end = primary_video.subclipped(0, min(primary_end_duration, primary_video.duration))
                if primary_end.duration < primary_end_duration:
                    # Loop primary if needed
                    loops_needed = int(primary_end_duration / primary_video.duration) + 1
                    primary_clips = [primary_video] * loops_needed
                    try:
                        from moviepy import concatenate_videoclips
                        looped_primary = concatenate_videoclips(primary_clips)
                        primary_end = looped_primary.subclipped(0, primary_end_duration)
                    except ImportError:
                        primary_end = primary_video.subclipped(0, min(primary_end_duration, primary_video.duration))
                
                # Concatenate all segments
                try:
                    from moviepy import concatenate_videoclips
                    final_clip = concatenate_videoclips([primary_start, secondary_segment, primary_end])
                    print("✅ Successfully created video sequence with secondary video")
                except ImportError:
                    print("⚠️ Could not concatenate videos, using primary only")
                    final_clip = primary_video.subclipped(0, min(audio_duration, primary_video.duration))
            else:
                print("Using primary video only...")
                # Use primary video for entire duration
                if primary_video.duration < audio_duration:
                    # Loop primary video to match audio duration
                    loops_needed = int(audio_duration / primary_video.duration) + 1
                    primary_clips = [primary_video] * loops_needed
                    try:
                        from moviepy import concatenate_videoclips
                        looped_primary = concatenate_videoclips(primary_clips)
                        final_clip = looped_primary.subclipped(0, audio_duration)
                    except ImportError:
                        final_clip = primary_video.subclipped(0, min(audio_duration, primary_video.duration))
                else:
                    final_clip = primary_video.subclipped(0, audio_duration)
            
            # Step 3: Add audio with BGM
            print("Adding audio with background music...")
            print(f"Original audio duration: {audio_clip.duration:.2f} seconds")
            mixed_audio = self.add_bgm_to_audio(audio_clip)
            print(f"Mixed audio duration: {mixed_audio.duration:.2f} seconds")
            final_clip = final_clip.with_audio(mixed_audio)
            
            # Step 4: Add heading if provided
            if self.heading_text.strip():
                print("Adding heading...")
                final_clip = add_heading(
                    final_clip,
                    text=self.heading_text,
                    font_size=65,
                    color="white",
                    padding_top=30,
                    padding_side=20
                )
            
            # Step 5: Add image overlays with animation
            if self.images_data:
                print(f"Adding {len(self.images_data)} image overlays...")
                for img_data in self.images_data:
                    try:
                        final_clip = add_image_overlay_with_animation(
                            final_clip, 
                            img_data['path'], 
                            start_time=img_data['start_time'], 
                            end_time=img_data['end_time'], 
                            padding=10
                        )
                        print(f"Added image: {os.path.basename(img_data['path'])}")
                    except Exception as e:
                        print(f"Error adding image {img_data['path']}: {e}")
            
            # Step 6: Add auto captions if generated
            if self.auto_captions:
                print("Adding auto captions...")
                try:
                    final_clip = add_captions(
                        final_clip,
                        texts=self.auto_captions['captions'],
                        start_times=self.auto_captions['start_times'],
                        durations=self.auto_captions['durations'],
                        color="white"
                    )
                except Exception as e:
                    print(f"Error adding auto captions: {e}")
            
            # Step 7: Add text overlays (smaller captions)
            if self.texts_data:
                print(f"Adding {len(self.texts_data)} text overlays...")
                try:
                    texts = [txt['content'] for txt in self.texts_data]
                    start_times = [txt['start_time'] for txt in self.texts_data]
                    end_times = [txt['end_time'] for txt in self.texts_data]
                    
                    final_clip = add_smaller_captions(
                        final_clip,
                        texts=texts,
                        start_times=start_times,
                        end_times=end_times,
                        font_size=38,
                        text_color="white",
                        bg_color="black",
                        bg_opacity=0.7,
                        padding_bottom=55,
                        padding_horizontal=35,
                        bg_padding=12,
                    )
                except Exception as e:
                    print(f"Error adding text overlays: {e}")
            
            # Step 8: Export video
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ultimate_short_{timestamp}.mp4"
            output_path = os.path.join("output_videos", output_filename)
            
            os.makedirs("output_videos", exist_ok=True)
            
            print(f"Exporting video to: {output_path}")
            
            # Export in 1080p with high quality settings (expand to fill instead of padding)
            final_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac",
                fps=30,
                preset="medium",
                ffmpeg_params=["-crf", "18", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"]
            )
            
            print("Video generation completed!")
            return output_path, f"✅ Video successfully created: {output_filename}\n✅ Auto-captions included: {len(self.auto_captions['captions']) if self.auto_captions else 0} captions"
            
        except Exception as e:
            print(f"Error during video generation: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, f"❌ Error generating video: {str(e)}"

# Initialize the editor
editor = UltimateShortEditor()

# Create the Gradio interface
def create_gradio_interface():
    with gr.Blocks(title="Ultimate Shorts Editor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎬 Ultimate Shorts Editor")
        gr.Markdown("Create amazing short videos with audio, videos, images, and text overlays!")
        gr.Markdown("**📝 Note:** Captions will be automatically generated when you click 'Generate Video'.")
        
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
                primary_video_status = gr.Textbox(label="Primary Video Status", interactive=False, lines=2)
            
            with gr.Column():
                gr.Markdown("### Secondary Video")
                secondary_video_input = gr.Video(label="Upload Secondary Video", height=250)
                secondary_video_btn = gr.Button("Add Secondary Video", variant="secondary")
                secondary_video_status = gr.Textbox(label="Secondary Video Status", interactive=False, lines=2)
        
        # Row 3: Heading
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📝 Heading")
                heading_input = gr.Textbox(label="Video Heading", placeholder="Enter heading...", lines=2)
                heading_btn = gr.Button("Update Heading", variant="primary")
                heading_status = gr.Textbox(label="Heading Status", interactive=False)
        
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
                gr.Markdown("## 🚀 Generate Video")
                gr.Markdown("*Captions will be automatically generated during video creation*")
                
                generate_btn = gr.Button("🎬 Generate Final Video", variant="primary", size="lg")
                
                final_video_output = gr.Video(label="Generated Video", height=400)
                generation_status = gr.Textbox(label="Generation Status", interactive=False)
        
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
            fn=editor.generate_final_video_simple,
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
