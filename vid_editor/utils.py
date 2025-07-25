import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
from typing import Dict, List, Tuple, Union, Optional, Any
import moviepy  # type: ignore
from moviepy import (  # type: ignore
    AudioFileClip, TextClip, CompositeVideoClip, VideoFileClip, VideoClip,
    vfx, ImageClip, concatenate_videoclips, CompositeAudioClip,
    concatenate_audioclips
)

# Import caption integration
try:
    from caption_integration import VideoCaptionIntegrator
    CAPTIONS_AVAILABLE = True
except ImportError:
    print("⚠️  Caption integration not available")
    CAPTIONS_AVAILABLE = False
    VideoCaptionIntegrator = None

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

def add_image_overlay(video: Union[VideoFileClip, CompositeVideoClip], image_path: str, start_time: float, duration: float = 5.0) -> CompositeVideoClip:
    """Add an image overlay to the video at a specific timestamp with slide-up entrance and slide-down exit"""
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return CompositeVideoClip([video])
    
    try:
        img_clip = ImageClip(image_path)
        
        video_width, video_height = video.size
        img_width, img_height = img_clip.size
        
        width_scale = (video_width * 0.75) / img_width
        height_scale = (video_height * 0.75) / img_height
        scale_factor = min(width_scale, height_scale)
        
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        
        img_clip = img_clip.resized((new_width, new_height))
        
        img_duration = min(duration, video.duration - start_time)
        if img_duration <= 0:
            print(f"Image at {start_time}s would appear after video ends.")
            return CompositeVideoClip([video])
        
        img_clip = img_clip.with_start(start_time).with_duration(img_duration)
        
        # Position the image in the center
        center_x = (video_width - new_width) // 2
        center_y = (video_height - new_height) // 2
        img_clip = img_clip.with_position((center_x, center_y))
        
        # Add fade effects for smooth entrance and exit
        fade_duration = min(0.5, img_duration / 4)
        img_clip = img_clip.with_effects([vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)])
        
        # For now, let's use a simple slide effect using moviepy's built-in capabilities
        # We'll create the slide effect by manipulating the position over time
        if img_duration > 1.0:  # Only animate if duration is long enough
            
            # Create slide-up entrance effect
            animation_duration = min(0.6, img_duration / 3)
            
            def slide_position(t):
                if t < animation_duration:
                    # Slide up from bottom
                    progress = t / animation_duration
                    # Ease-out effect
                    progress = 1 - (1 - progress) ** 2
                    # Start from below screen
                    start_y = video_height
                    current_y = start_y - (start_y - center_y) * progress
                    return (center_x, max(0, min(video_height, int(current_y))))
                elif t > img_duration - animation_duration:
                    # Slide down to bottom
                    exit_progress = (t - (img_duration - animation_duration)) / animation_duration
                    # Ease-in effect
                    exit_progress = exit_progress ** 2
                    # Move to below screen
                    end_y = video_height
                    current_y = center_y + (end_y - center_y) * exit_progress
                    return (center_x, max(0, min(video_height, int(current_y))))
                else:
                    # Stay in center
                    return (center_x, center_y)
            
            # Apply the slide animation
            img_clip = img_clip.with_position(slide_position)
        
        result = CompositeVideoClip([video, img_clip])
        return result
    
    except Exception as e:
        print(f"Error adding image overlay: {e}")
        return CompositeVideoClip([video])

def add_text_overlay(video: Union[VideoFileClip, CompositeVideoClip], text: str, start_time: float, duration: float = 3.0) -> CompositeVideoClip:
    """Add a text overlay to the video at a specific timestamp"""
    try:
        font_path = "static/Utendo-Bold.ttf"
        
        # Calculate text width as integer
        text_width = int(video.size[0] * 0.8)
        
        text_clip = TextClip(
            text=text,
            font=font_path,
            font_size=40,
            color='white',
            bg_color=None,
            method='caption',
            size=(text_width, None)
        )
        
        text_duration = min(duration, video.duration - start_time)
        if text_duration <= 0:
            print(f"Text at {start_time}s would appear after video ends.")
            return CompositeVideoClip([video])
        
        # Position text at 30% from bottom (70% from top)
        vertical_position = int(video.size[1] * 0.7)
        text_clip = text_clip.with_position(('center', vertical_position)).with_start(start_time).with_duration(text_duration)
        
        result = CompositeVideoClip([video, text_clip])
        return result
    
    except Exception as e:
        print(f"Error adding text overlay: {e}")
        return CompositeVideoClip([video])

def add_captions_from_audio(video: Union[VideoFileClip, CompositeVideoClip], audio_path: str, font_path: Optional[str] = None, word_by_word: bool = True) -> CompositeVideoClip:
    """Add auto-generated captions from audio file to video
    
    Args:
        video: Video to add captions to
        audio_path: Path to audio file for caption generation
        font_path: Path to font file (optional)
        word_by_word: Whether to show captions one word at a time (default: True)
    """
    if not CAPTIONS_AVAILABLE or VideoCaptionIntegrator is None:
        print("📝 Caption integration not available - skipping captions")
        return CompositeVideoClip([video])
    
    if not os.path.exists(audio_path):
        print(f"Audio file not found for captions: {audio_path}")
        return CompositeVideoClip([video])
    
    try:
        caption_mode = "word-by-word" if word_by_word else "full-text"
        print(f"🎤 Generating captions from audio ({caption_mode})...")
        
        # Initialize caption integrator
        integrator = VideoCaptionIntegrator(model_size="base")
        
        # Use the same font as text overlays
        if font_path is None:
            font_path = "static/Utendo-Bold.ttf"
        
        # Add captions to video with configurable word-by-word display
        result = integrator.add_captions_to_video(
            video=video,
            audio_path=audio_path,
            font_path=font_path if os.path.exists(font_path) else None,
            font_size=32,  # Slightly smaller than manual text overlays
            font_color='white',
            word_by_word=word_by_word
        )
        
        print("✅ Captions added successfully")
        return result
        
    except Exception as e:
        print(f"Error adding captions from audio: {e}")
        return CompositeVideoClip([video])

def combine_videos(primary_video_path: str, secondary_video_path: str | None = None) -> Union[VideoFileClip, CompositeVideoClip]:
    """Combine two videos (optional) into one clip"""
    if not os.path.exists(primary_video_path):
        raise FileNotFoundError(f"Primary video file not found: {primary_video_path}")
    
    primary_clip = VideoFileClip(primary_video_path)
    
    if secondary_video_path and os.path.exists(secondary_video_path):
        secondary_clip = VideoFileClip(secondary_video_path)
        secondary_clip = secondary_clip.resized(primary_clip.size)
        concatenated = concatenate_videoclips([primary_clip, secondary_clip])
        # Type cast for return type compatibility
        return concatenated if isinstance(concatenated, VideoFileClip) else primary_clip
    
    return primary_clip

def add_audio(video: Union[VideoFileClip, CompositeVideoClip], overlay_audio_path: str | None = None, background_audio_path: str | None = None) -> Union[VideoFileClip, CompositeVideoClip]:
    """Add overlay and/or background audio to video"""
    result_video = video
    
    if overlay_audio_path and os.path.exists(overlay_audio_path):
        try:
            overlay_audio = AudioFileClip(overlay_audio_path)
            if overlay_audio.duration > video.duration:
                overlay_audio = overlay_audio.subclipped(0, video.duration)
            else:
                repeats = int(np.ceil(video.duration / overlay_audio.duration))
                overlay_audio = AudioFileClip(overlay_audio_path).with_volume_scaled(0.7)
                overlay_audio = concatenate_audioclips([overlay_audio] * repeats).subclipped(0, video.duration)
            
            if result_video.audio:
                original_audio = result_video.audio.with_volume_scaled(0.3)
                result_video = result_video.with_audio(
                    CompositeAudioClip([original_audio, overlay_audio])
                )
            else:
                result_video = result_video.with_audio(overlay_audio)
                
        except Exception as e:
            print(f"Error adding overlay audio: {e}")
    
    if background_audio_path and os.path.exists(background_audio_path):
        try:
            bg_audio = AudioFileClip(background_audio_path)
            bg_audio = bg_audio.with_volume_scaled(0.15)

            if bg_audio.duration > video.duration:
                bg_audio = bg_audio.subclipped(0, video.duration)
            else:
                repeats = int(np.ceil(video.duration / bg_audio.duration))
                bg_audio = concatenate_audioclips([bg_audio] * repeats).subclipped(0, video.duration)
            
            if result_video.audio:
                result_video = result_video.with_audio(
                    CompositeAudioClip([result_video.audio, bg_audio])
                )
            else:
                result_video = result_video.with_audio(bg_audio)
                
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
        thumbnail_time = video.duration / 3
        frame = video.get_frame(thumbnail_time)
        
        if frame is not None:
            img = Image.fromarray(frame)
            
            if text:
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("static/Utendo-Bold.ttf", size=40)
                except Exception:
                    print("Warning: Could not load custom font, using default")
                    font = ImageFont.load_default()
                    
                text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
                position = ((img.width - text_width) // 2, (img.height - text_height) // 2)

                outline_color = (0, 0, 0)
                text_color = (255, 255, 255)
                
                for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    draw.text((position[0] + offset[0], position[1] + offset[1]), text, font=font, fill=outline_color)
                    
                draw.text(position, text, font=font, fill=text_color)
            
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            img.save(output_path, quality=95)
            return output_path
        else:
            raise ValueError("Could not extract frame from video")
        
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        raise
    finally:
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
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        video = VideoFileClip(video_path)
        
        preview_duration = min(duration, video.duration)
        preview = video.subclipped(0, preview_duration)
        
        try:
            text_clip = TextClip(
                text="PREVIEW",
                font="static/Utendo-Bold.ttf",
                font_size=24,
                color='white',
                bg_color=None,
                method='label'
            ).with_position(('right', 'top')).with_duration(preview_duration)
        except Exception:
            # Fall back to default font if custom font fails
            text_clip = TextClip(
                text="PREVIEW",
                font_size=24,
                color='white',
                bg_color=None,
                method='label'
            ).with_position(('right', 'top')).with_duration(preview_duration)
        
        preview = CompositeVideoClip([preview, text_clip])
        
        preview.write_videofile(
            output_path, 
            codec="h264", 
            audio_codec="aac", 
            bitrate="1500k", 
            fps=30,
            logger=None
        )
        
        return output_path
        
    except Exception as e:
        print(f"Error creating preview: {e}")
        return None
    finally:
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
        if video:
            try:
                video.close()
            except Exception:
                pass

def create_video_transition(clip1: VideoFileClip, clip2: VideoFileClip, transition_duration: float = 1.0, 
                         transition_type: str = "crossfade") -> VideoClip:
    """Create a smooth transition between two video clips
    
    Args:
        clip1: First video clip
        clip2: Second video clip
        transition_duration: Duration of the transition effect in seconds
        transition_type: Type of transition effect (crossfade, fade, etc.)
        
    Returns:
        VideoFileClip with the transition effect
    """
    max_transition = min(clip1.duration, clip2.duration) / 2
    transition_duration = min(transition_duration, max_transition)
    
    if transition_type == "crossfade":
        clip1_faded = clip1.with_effects([vfx.CrossFadeOut(transition_duration)])
        clip2_faded = clip2.with_effects([vfx.CrossFadeIn(transition_duration)])
        
        result = concatenate_videoclips([
            clip1_faded.subclipped(0, clip1.duration - transition_duration/2),
            clip2_faded.subclipped(transition_duration/2, clip2.duration)
        ])
        return result
        
    elif transition_type == "fade":
        clip1_faded = clip1.with_effects([vfx.FadeOut(transition_duration)])
        clip2_faded = clip2.with_effects([vfx.FadeIn(transition_duration)])
        result = concatenate_videoclips([clip1_faded, clip2_faded])
        return result
    
    else:
        result = concatenate_videoclips([clip1, clip2])
        return result

def add_text_with_animation(video: Union[VideoFileClip, CompositeVideoClip], text: str, start_time: float, 
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
                text_align='center'
            )
        except Exception:
            text_clip = TextClip(
                text=text,
                font_size=40,
                color='white',
                bg_color=None,
                method='caption',
                size=(video.size[0] * 0.8, None),
                text_align='center'
            )
        
        text_duration = min(duration, video.duration - start_time)
        if text_duration <= 0:
            print(f"Text at {start_time}s would appear after video ends.")
            return CompositeVideoClip([video]) if isinstance(video, VideoFileClip) else video
            
        text_clip = text_clip.with_position(('center', 'center')).with_start(start_time).with_duration(text_duration)
        
        anim_duration = min(0.7, text_duration / 4)
        
        if animation == "slide":
            text_clip = text_clip.with_effects([vfx.SlideIn(anim_duration, 'bottom'), vfx.SlideOut(anim_duration, 'bottom')])
            
        elif animation == "fade":
            text_clip = text_clip.fadein(anim_duration).fadeout(anim_duration)
            
        elif animation == "zoom":
            # ZoomIn/ZoomOut might not be available in all versions, use resize instead
            try:
                text_clip = text_clip.with_effects([vfx.Resize(lambda t: 1 + 0.1 * (1 - abs(2*t/text_duration - 1)))])
            except AttributeError:
                # Fallback to fade if zoom effects aren't available
                text_clip = text_clip.with_effects([vfx.FadeIn(anim_duration), vfx.FadeOut(anim_duration)])
            
        elif animation == "typewriter":
            # Simplified typewriter effect since complex make_frame approach has changed
            def make_typewriter_text(t):
                progress = min(1.0, t / (text_duration - anim_duration))
                char_count = max(1, int(len(text) * progress))
                return text[:char_count]
            
            try:
                text_clip = TextClip(
                    text=text,
                    font=font_path if os.path.exists(font_path) else None,
                    font_size=40,
                    color='white',
                    bg_color=None,
                    method='caption',
                    size=(video.size[0] * 0.8, None),
                    text_align='center',
                    duration=text_duration
                ).with_position(('center', 'center')).with_start(start_time)
            except Exception:
                # Fallback to simple fade if typewriter fails
                text_clip = text_clip.with_effects([vfx.FadeIn(anim_duration), vfx.FadeOut(anim_duration)])
        
        result = CompositeVideoClip([video, text_clip])
        return result
    
    except Exception as e:
        print(f"Error adding animated text: {e}")
        return CompositeVideoClip([video]) if isinstance(video, VideoFileClip) else video

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
            def cinematic_filter(frame):
                frame_float = frame.astype(np.float32) / 255.0
                
                contrast = 1.2
                saturation = 1.1
                
                frame_float = (frame_float - 0.5) * contrast + 0.5
                
                shadows = np.minimum(frame_float, 0.5) / 0.5
                highlights = np.maximum(frame_float - 0.5, 0) / 0.5
                
                shadows_tinted = shadows.copy()
                shadows_tinted[:,:,0] *= 0.9
                shadows_tinted[:,:,2] *= 1.1
                
                highlights_tinted = highlights.copy()
                highlights_tinted[:,:,0] *= 1.1
                highlights_tinted[:,:,2] *= 0.9
                
                frame_float = shadows_tinted * 0.5 + highlights_tinted * 0.5
                
                luminance = 0.299 * frame_float[:,:,0] + 0.587 * frame_float[:,:,1] + 0.114 * frame_float[:,:,2]
                luminance = luminance.reshape(frame_float.shape[0], frame_float.shape[1], 1)
                frame_float = luminance + saturation * (frame_float - luminance)
                
                frame_result = np.clip(frame_float * 255.0, 0, 255).astype(np.uint8)
                return frame_result
                
            return video.image_transform(cinematic_filter)
            
        elif style == "warm":
            def warm_filter(frame):
                frame_float = frame.astype(np.float32)
                frame_float[:,:,0] = np.minimum(frame_float[:,:,0] * 1.15, 255)
                frame_float[:,:,1] = np.minimum(frame_float[:,:,1] * 1.05, 255)
                frame_float[:,:,2] = np.maximum(frame_float[:,:,2] * 0.9, 0)
                return frame_float.astype(np.uint8)
                
            return video.image_transform(warm_filter)
            
        elif style == "cold":
            def cold_filter(frame):
                frame_float = frame.astype(np.float32)
                frame_float[:,:,0] = np.maximum(frame_float[:,:,0] * 0.9, 0)
                frame_float[:,:,2] = np.minimum(frame_float[:,:,2] * 1.15, 255)
                return frame_float.astype(np.uint8)
                
            return video.image_transform(cold_filter)
            
        elif style == "vintage":
            def vintage_filter(frame):
                frame_float = frame.astype(np.float32)
                
                r = frame_float[:,:,0] * 0.393 + frame_float[:,:,1] * 0.769 + frame_float[:,:,2] * 0.189
                g = frame_float[:,:,0] * 0.349 + frame_float[:,:,1] * 0.686 + frame_float[:,:,2] * 0.168
                b = frame_float[:,:,0] * 0.272 + frame_float[:,:,1] * 0.534 + frame_float[:,:,2] * 0.131
                
                frame_float[:,:,0] = np.minimum(r, 255)
                frame_float[:,:,1] = np.minimum(g, 255)
                frame_float[:,:,2] = np.minimum(b, 255)
                
                rows, cols = frame.shape[:2]
                center_x, center_y = cols / 2, rows / 2
                
                y, x = np.ogrid[:rows, :cols]
                mask = ((x - center_x)**2 + (y - center_y)**2) / (max(center_x, center_y)**2)
                mask = np.minimum(mask * 1.5, 1.0)
                
                for c in range(3):
                    frame_float[:,:,c] = frame_float[:,:,c] * (1.0 - mask * 0.6)
                
                return np.clip(frame_float, 0, 255).astype(np.uint8)
                
            return video.image_transform(vintage_filter)
            
        else:
            return video
            
    except Exception as e:
        print(f"Error applying color grading: {e}")
        return video