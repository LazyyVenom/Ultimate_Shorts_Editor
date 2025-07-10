import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
from typing import Dict, List, Tuple, Union, Optional, Any
import moviepy.editor  # type: ignore
from moviepy.editor import (  # type: ignore
    AudioFileClip, TextClip, CompositeVideoClip, VideoFileClip,
    vfx, ImageClip, concatenate_videoclips, CompositeAudioClip
)

def add_heading(video: VideoFileClip, heading: str) -> CompositeVideoClip:
    text_clip = TextClip(
        text=heading,
        font=r"static/Utendo-Bold.ttf",
        font_size=57,
        color='white',
        bg_color='black',
        size=(video.size[0], None),
        duration=video.duration,
        text_align="center",
        margin=(None, 25),
        method="caption",
        interline=25,
        vertical_align="top",
    ).with_start(0)

    fade_duration = min(1, video.duration / 5)
    text_clip = text_clip.with_effects([vfx.SlideIn(fade_duration, 'top'), vfx.SlideOut(fade_duration, 'top')])

    video_with_text = CompositeVideoClip([video, text_clip])
    return video_with_text

def add_image_overlay(video: VideoFileClip, image_path: str, start_time: float, duration: float = 5.0) -> CompositeVideoClip:
    """Add an image overlay to the video at a specific timestamp"""
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return video
    
    try:
        # Load the image
        img_clip = ImageClip(image_path)
        
        # Scale the image to fit within the video frame (maintain aspect ratio)
        video_width, video_height = video.size
        img_width, img_height = img_clip.size
        
        # Calculate scale factor to fit within 75% of the video dimensions
        width_scale = (video_width * 0.75) / img_width
        height_scale = (video_height * 0.75) / img_height
        scale_factor = min(width_scale, height_scale)
        
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        
        img_clip = img_clip.resize((new_width, new_height))
        
        # Center the image on the screen
        img_clip = img_clip.set_position(('center', 'center'))
        
        # Set the duration and start time
        img_duration = min(duration, video.duration - start_time)
        if img_duration <= 0:
            print(f"Image at {start_time}s would appear after video ends.")
            return video
        
        img_clip = img_clip.set_start(start_time).set_duration(img_duration)
        
        # Add fade in/out effect
        fade_duration = min(0.5, img_duration / 4)
        img_clip = img_clip.fadein(fade_duration).fadeout(fade_duration)
        
        # Overlay the image on the video
        result = CompositeVideoClip([video, img_clip])
        return result
    
    except Exception as e:
        print(f"Error adding image overlay: {e}")
        return video

def add_text_overlay(video: VideoFileClip, text: str, start_time: float, duration: float = 3.0) -> CompositeVideoClip:
    """Add a text overlay to the video at a specific timestamp"""
    try:
        # Create a text clip
        font_path = "static/Utendo-Bold.ttf"
        text_clip = TextClip(
            text=text,
            font=font_path,
            font_size=40,
            color='white',
            bg_color=None,
            method='caption',
            size=(video.size[0] * 0.8, None),
            align='center'
        )
        
        # Set the duration and start time
        text_duration = min(duration, video.duration - start_time)
        if text_duration <= 0:
            print(f"Text at {start_time}s would appear after video ends.")
            return video
        
        text_clip = text_clip.set_position(('center', 'bottom')).set_start(start_time).set_duration(text_duration)
        
        # Add fade in/out effect
        fade_duration = min(0.5, text_duration / 4)
        text_clip = text_clip.fadein(fade_duration).fadeout(fade_duration)
        
        # Overlay the text on the video
        result = CompositeVideoClip([video, text_clip])
        return result
    
    except Exception as e:
        print(f"Error adding text overlay: {e}")
        return video

def combine_videos(primary_video_path: str, secondary_video_path: str | None = None) -> VideoFileClip:
    """Combine two videos (optional) into one clip"""
    if not os.path.exists(primary_video_path):
        raise FileNotFoundError(f"Primary video file not found: {primary_video_path}")
    
    primary_clip = VideoFileClip(primary_video_path)
    
    if secondary_video_path and os.path.exists(secondary_video_path):
        secondary_clip = VideoFileClip(secondary_video_path)
        # Resize secondary clip to match primary dimensions
        secondary_clip = secondary_clip.resize(primary_clip.size)
        # Combine the clips (concatenate)
        return concatenate_videoclips([primary_clip, secondary_clip])
    
    return primary_clip

def add_audio(video: VideoFileClip, overlay_audio_path: str | None = None, background_audio_path: str | None = None) -> VideoFileClip:
    """Add overlay and/or background audio to video"""
    result_video = video
    
    # Add overlay audio if provided
    if overlay_audio_path and os.path.exists(overlay_audio_path):
        try:
            overlay_audio = AudioFileClip(overlay_audio_path)
            # Trim or loop the overlay audio to match video duration
            if overlay_audio.duration > video.duration:
                overlay_audio = overlay_audio.subclip(0, video.duration)
            else:
                # Loop audio to match video duration
                repeats = int(np.ceil(video.duration / overlay_audio.duration))
                overlay_audio = AudioFileClip(overlay_audio_path).volumex(0.7)
                overlay_audio = concatenate_videoclips([overlay_audio] * repeats).subclip(0, video.duration)
            
            # Mix overlay audio with existing audio
            if result_video.audio:
                original_audio = result_video.audio.volumex(0.3)  # Lower original volume
                result_video = result_video.set_audio(
                    CompositeAudioClip([original_audio, overlay_audio])
                )
            else:
                result_video = result_video.set_audio(overlay_audio)
                
        except Exception as e:
            print(f"Error adding overlay audio: {e}")
    
    # Add background audio if provided
    if background_audio_path and os.path.exists(background_audio_path):
        try:
            bg_audio = AudioFileClip(background_audio_path)
            # Set background audio volume lower than overlay
            bg_audio = bg_audio.volumex(0.15)  # Low volume for background
            
            # Trim or loop the background audio to match video duration
            if bg_audio.duration > video.duration:
                bg_audio = bg_audio.subclip(0, video.duration)
            else:
                # Loop audio to match video duration
                repeats = int(np.ceil(video.duration / bg_audio.duration))
                bg_audio = concatenate_videoclips([bg_audio] * repeats).subclip(0, video.duration)
            
            # Mix background audio with existing audio
            if result_video.audio:
                result_video = result_video.set_audio(
                    CompositeAudioClip([result_video.audio, bg_audio])
                )
            else:
                result_video = result_video.set_audio(bg_audio)
                
        except Exception as e:
            print(f"Error adding background audio: {e}")
    
    return result_video

def generate_thumbnail(video_path: str, output_path: str, text: Optional[str] = None) -> str:
    """Generate a thumbnail from a video with optional text overlay
    
    Args:
        video_path: Path to the video file
        output_path: Path where the thumbnail should be saved
        text: Optional text to overlay on the thumbnail
        
    Returns:
        Path to the generated thumbnail
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    video = VideoFileClip(video_path)
    
    try:
        # Take frame from 1/3 of the video duration
        thumbnail_time = video.duration / 3
        frame = video.get_frame(thumbnail_time)
        
        # Convert to PIL Image for processing
        img = Image.fromarray(frame)
        
        # Add text overlay if provided
        if text:
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("static/Utendo-Bold.ttf", size=40)
            except Exception:
                print("Warning: Could not load custom font, using default")
                font = ImageFont.load_default()
                
            # Calculate text position (centered)
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
            position = ((img.width - text_width) // 2, (img.height - text_height) // 2)
            
            # Add text with outline for better visibility
            outline_color = (0, 0, 0)  # Black outline
            text_color = (255, 255, 255)  # White text
            
            # Draw text outline
            for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                draw.text((position[0] + offset[0], position[1] + offset[1]), text, font=font, fill=outline_color)
                
            # Draw main text
            draw.text(position, text, font=font, fill=text_color)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Save the thumbnail
        img.save(output_path, quality=95)
        return output_path
        
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        raise
    finally:
        # Always close the video file to avoid resource leaks
        video.close()

def create_video_preview(video_path: str, output_path: str, duration: float = 5) -> Optional[str]:
    """Create a short preview clip from a video
    
    Args:
        video_path: Path to the video file
        output_path: Path where the preview should be saved
        duration: Duration of the preview in seconds
        
    Returns:
        Path to the generated preview or None if an error occurs
    """
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return None
    
    video = None
    preview = None
    try:
        # Create directory for output if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Load the video
        video = VideoFileClip(video_path)
        
        # Create a short clip from the first few seconds
        preview_duration = min(duration, video.duration)
        preview = video.subclip(0, preview_duration)
        
        # Add a "Preview" label to distinguish it
        try:
            text_clip = TextClip(
                text="PREVIEW",
                font="static/Utendo-Bold.ttf",
                font_size=24,
                color='white',
                bg_color=None,
                method='label'
            ).set_position(('right', 'top')).set_duration(preview_duration)
        except Exception:
            # Fall back to default font if custom font fails
            text_clip = TextClip(
                text="PREVIEW",
                font_size=24,
                color='white',
                bg_color=None,
                method='label'
            ).set_position(('right', 'top')).set_duration(preview_duration)
        
        # Combine the preview and text
        preview = CompositeVideoClip([preview, text_clip])
        
        # Write the preview file with progress monitor
        preview.write_videofile(
            output_path, 
            codec="h264", 
            audio_codec="aac", 
            bitrate="1500k", 
            fps=30,
            logger=None  # Suppress verbose output
        )
        
        return output_path
        
    except Exception as e:
        print(f"Error creating preview: {e}")
        return None
    finally:
        # Clean up resources
        if video:
            try:
                video.close()
            except Exception:
                pass
        if preview:
            try:
                preview.close()
            except Exception:
                pass

def get_video_info(video_path: str) -> Optional[Dict[str, Any]]:
    """Get video information like duration, resolution, etc.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary with video information or None if an error occurs
    """
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return None
    
    video = None
    try:
        video = VideoFileClip(video_path)
        info = {
            'duration': video.duration,
            'width': video.size[0],
            'height': video.size[1],
            'fps': video.fps,
            'audio': video.audio is not None,
            'filename': os.path.basename(video_path),
            'filesize_mb': os.path.getsize(video_path) / (1024 * 1024)
        }
        return info
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None
    finally:
        # Ensure we close the video to prevent resource leaks
        if video:
            try:
                video.close()
            except Exception:
                pass

def create_video_transition(clip1: VideoFileClip, clip2: VideoFileClip, transition_duration: float = 1.0, 
                         transition_type: str = "crossfade") -> VideoFileClip:
    """Create a smooth transition between two video clips
    
    Args:
        clip1: First video clip
        clip2: Second video clip
        transition_duration: Duration of the transition effect in seconds
        transition_type: Type of transition effect (crossfade, fade, etc.)
        
    Returns:
        VideoFileClip with the transition effect
    """
    # Adjust transition duration to be within limits
    max_transition = min(clip1.duration, clip2.duration) / 2
    transition_duration = min(transition_duration, max_transition)
    
    if transition_type == "crossfade":
        # Create crossfade transition
        clip1 = clip1.crossfadeout(transition_duration)
        clip2 = clip2.crossfadein(transition_duration)
        
        # Combine with a slight overlap for the transition
        result = concatenate_videoclips([
            clip1.subclip(0, clip1.duration - transition_duration/2),
            clip2.subclip(transition_duration/2)
        ])
        return result
        
    elif transition_type == "fade":
        # Simple fade transition
        clip1 = clip1.fadeout(transition_duration)
        clip2 = clip2.fadein(transition_duration)
        return concatenate_videoclips([clip1, clip2])
    
    else:
        # Default to simple concatenation if transition type not recognized
        return concatenate_videoclips([clip1, clip2])

def add_text_with_animation(video: VideoFileClip, text: str, start_time: float, 
                            duration: float = 3.0, animation: str = "slide") -> CompositeVideoClip:
    """Add animated text overlay to the video
    
    Args:
        video: Base video clip
        text: Text to display
        start_time: When to start displaying the text (seconds)
        duration: How long to display the text (seconds)
        animation: Animation type ("slide", "fade", "zoom", "typewriter")
        
    Returns:
        CompositeVideoClip with the animated text
    """
    try:
        # Create a text clip
        font_path = "static/Utendo-Bold.ttf"
        
        try:
            text_clip = TextClip(
                text=text,
                font=font_path,
                font_size=40,
                color='white',
                bg_color=None,
                method='caption',
                size=(video.size[0] * 0.8, None),
                align='center'
            )
        except Exception:
            # Fall back to default font if custom font fails
            text_clip = TextClip(
                text=text,
                font_size=40,
                color='white',
                bg_color=None,
                method='caption',
                size=(video.size[0] * 0.8, None),
                align='center'
            )
        
        # Set the duration and start time
        text_duration = min(duration, video.duration - start_time)
        if text_duration <= 0:
            print(f"Text at {start_time}s would appear after video ends.")
            return video
            
        # Position the text
        text_clip = text_clip.set_position(('center', 'center')).set_start(start_time).set_duration(text_duration)
        
        # Apply animation based on type
        anim_duration = min(0.7, text_duration / 4)
        
        if animation == "slide":
            # Slide from bottom
            text_clip = text_clip.with_effects([vfx.SlideIn(anim_duration, 'bottom'), vfx.SlideOut(anim_duration, 'bottom')])
            
        elif animation == "fade":
            # Fade in/out
            text_clip = text_clip.fadein(anim_duration).fadeout(anim_duration)
            
        elif animation == "zoom":
            # Zoom effect
            text_clip = text_clip.with_effects([vfx.ZoomIn(anim_duration), vfx.ZoomOut(anim_duration)])
            
        elif animation == "typewriter":
            # Simple typewriter effect (frame by frame)
            def make_typewriter_frame(t):
                # Calculate how much text to show based on time
                progress = min(1.0, t / (text_duration - anim_duration))
                char_count = max(1, int(len(text) * progress))
                current_text = text[:char_count]
                
                # Create a frame with the current text
                txt_frame = TextClip(
                    text=current_text,
                    font=font_path if os.path.exists(font_path) else None,
                    font_size=40,
                    color='white',
                    bg_color=None,
                    method='caption',
                    size=(video.size[0] * 0.8, None),
                    align='center'
                ).set_position(('center', 'center'))
                
                return txt_frame.img
                
            # Create the typewriter effect
            text_clip = VideoFileClip(
                make_frame=make_typewriter_frame,
                duration=text_duration
            ).set_start(start_time)
        
        # Overlay the text on the video
        result = CompositeVideoClip([video, text_clip])
        return result
    
    except Exception as e:
        print(f"Error adding animated text: {e}")
        return video

def apply_color_grading(video: VideoFileClip, style: str = "cinematic") -> VideoFileClip:
    """Apply color grading effect to a video
    
    Args:
        video: Input video clip
        style: Color grading style ("cinematic", "warm", "cold", "vintage")
        
    Returns:
        Video with color grading applied
    """
    try:
        if style == "cinematic":
            # Cinematic look (higher contrast, slightly blue shadows, warm highlights)
            def cinematic_filter(frame):
                # Convert to float for processing
                frame_float = frame.astype(np.float32) / 255.0
                
                # Apply color adjustments
                contrast = 1.2  # Increase contrast
                saturation = 1.1  # Slightly increase saturation
                
                # Apply contrast
                frame_float = (frame_float - 0.5) * contrast + 0.5
                
                # Apply color tinting to shadows and highlights
                # Shadows slightly blue, highlights slightly warm
                shadows = np.minimum(frame_float, 0.5) / 0.5
                highlights = np.maximum(frame_float - 0.5, 0) / 0.5
                
                # Blue shadows
                shadows_tinted = shadows.copy()
                shadows_tinted[:,:,0] *= 0.9  # Reduce red in shadows
                shadows_tinted[:,:,2] *= 1.1  # Increase blue in shadows
                
                # Warm highlights
                highlights_tinted = highlights.copy()
                highlights_tinted[:,:,0] *= 1.1  # Increase red in highlights
                highlights_tinted[:,:,2] *= 0.9  # Reduce blue in highlights
                
                # Combine shadows and highlights
                frame_float = shadows_tinted * 0.5 + highlights_tinted * 0.5
                
                # Apply saturation
                luminance = 0.299 * frame_float[:,:,0] + 0.587 * frame_float[:,:,1] + 0.114 * frame_float[:,:,2]
                luminance = luminance.reshape(frame_float.shape[0], frame_float.shape[1], 1)
                frame_float = luminance + saturation * (frame_float - luminance)
                
                # Convert back to uint8
                frame_result = np.clip(frame_float * 255.0, 0, 255).astype(np.uint8)
                return frame_result
                
            return video.fl_image(cinematic_filter)
            
        elif style == "warm":
            # Warm look (increase reds and yellows)
            def warm_filter(frame):
                frame_float = frame.astype(np.float32)
                # Increase red and green (yellow) channels
                frame_float[:,:,0] = np.minimum(frame_float[:,:,0] * 1.15, 255)  # Red
                frame_float[:,:,1] = np.minimum(frame_float[:,:,1] * 1.05, 255)  # Green
                frame_float[:,:,2] = np.maximum(frame_float[:,:,2] * 0.9, 0)     # Blue
                return frame_float.astype(np.uint8)
                
            return video.fl_image(warm_filter)
            
        elif style == "cold":
            # Cold look (increase blues)
            def cold_filter(frame):
                frame_float = frame.astype(np.float32)
                # Increase blue channel, reduce red
                frame_float[:,:,0] = np.maximum(frame_float[:,:,0] * 0.9, 0)     # Red
                frame_float[:,:,2] = np.minimum(frame_float[:,:,2] * 1.15, 255)  # Blue
                return frame_float.astype(np.uint8)
                
            return video.fl_image(cold_filter)
            
        elif style == "vintage":
            # Vintage look (sepia tone with vignette)
            def vintage_filter(frame):
                # Convert to sepia
                frame_float = frame.astype(np.float32)
                
                # Create sepia tone
                r = frame_float[:,:,0] * 0.393 + frame_float[:,:,1] * 0.769 + frame_float[:,:,2] * 0.189
                g = frame_float[:,:,0] * 0.349 + frame_float[:,:,1] * 0.686 + frame_float[:,:,2] * 0.168
                b = frame_float[:,:,0] * 0.272 + frame_float[:,:,1] * 0.534 + frame_float[:,:,2] * 0.131
                
                frame_float[:,:,0] = np.minimum(r, 255)
                frame_float[:,:,1] = np.minimum(g, 255)
                frame_float[:,:,2] = np.minimum(b, 255)
                
                # Add vignette effect (darker corners)
                rows, cols = frame.shape[:2]
                center_x, center_y = cols / 2, rows / 2
                
                # Create radial gradient mask
                y, x = np.ogrid[:rows, :cols]
                mask = ((x - center_x)**2 + (y - center_y)**2) / (max(center_x, center_y)**2)
                mask = np.minimum(mask * 1.5, 1.0)
                
                # Apply vignette
                for c in range(3):
                    frame_float[:,:,c] = frame_float[:,:,c] * (1.0 - mask * 0.6)
                
                return np.clip(frame_float, 0, 255).astype(np.uint8)
                
            return video.fl_image(vintage_filter)
            
        else:
            # Return original if style not recognized
            return video
            
    except Exception as e:
        print(f"Error applying color grading: {e}")
        return video