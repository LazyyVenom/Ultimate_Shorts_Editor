"""
Audio Captioning Module using Faster-Whisper
Generates Hinglish captions from audio files with timestamps
"""

import os
import json
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import tempfile
import subprocess

try:
    from faster_whisper import WhisperModel
except ImportError:
    raise ImportError("faster-whisper not installed. Install with: pip install faster-whisper")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HinglishCaptioner:
    """
    A class to generate Hinglish captions from audio files using Faster-Whisper
    """
    
    def __init__(self, model_size: str = "medium", device: str = "auto", compute_type: str = "auto"):
        """
        Initialize the captioner with specified model parameters
        
        Args:
            model_size: Size of the Whisper model (tiny, base, small, medium, large-v1, large-v2, large-v3)
            device: Device to run on ("cpu", "cuda", "auto")
            compute_type: Compute precision ("int8", "int16", "float16", "float32", "auto")
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Faster-Whisper model"""
        try:
            logger.info(f"Loading Faster-Whisper {self.model_size} model...")
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def extract_audio_from_video(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video file using ffmpeg
        
        Args:
            video_path: Path to the video file
            output_path: Path for the extracted audio (optional)
            
        Returns:
            Path to the extracted audio file
        """
        if output_path is None:
            # Create temporary audio file
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"extracted_audio_{os.getpid()}.wav")
        
        try:
            # Use ffmpeg to extract audio
            cmd = [
                "ffmpeg", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", 
                "-ar", "16000", "-ac", "1", 
                "-y", output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            logger.info(f"Audio extracted to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            raise
    
    def transcribe_audio(
        self, 
        audio_path: str, 
        language: str = "hi",  # Hindi for Hinglish
        task: str = "transcribe",
        vad_filter: bool = True,
        vad_parameters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Transcribe audio file and return segments with timestamps
        
        Args:
            audio_path: Path to the audio file
            language: Language code (hi for Hindi/Hinglish)
            task: "transcribe" or "translate"
            vad_filter: Enable voice activity detection
            vad_parameters: VAD parameters dictionary
            
        Returns:
            List of caption segments with timestamps
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if vad_parameters is None:
            vad_parameters = {
                "threshold": 0.5,
                "min_speech_duration_ms": 250,
                "max_speech_duration_s": 30,
                "min_silence_duration_ms": 100,
                "speech_pad_ms": 400
            }
        
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe with Faster-Whisper
            if self.model is None:
                raise RuntimeError("Model not loaded")
                
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                vad_filter=vad_filter,
                vad_parameters=vad_parameters,
                word_timestamps=True
            )
            
            logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            # Process segments
            captions = []
            for segment in segments:
                caption_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "words": []
                }
                
                # Add word-level timestamps if available
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        caption_data["words"].append({
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability
                        })
                
                captions.append(caption_data)
            
            logger.info(f"Generated {len(captions)} caption segments")
            return captions
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def format_captions_for_video(
        self, 
        captions: List[Dict], 
        max_chars_per_line: int = 40,
        max_lines: int = 2
    ) -> List[Dict]:
        """
        Format captions for video display with proper line breaks
        
        Args:
            captions: List of caption segments
            max_chars_per_line: Maximum characters per line
            max_lines: Maximum lines per caption
            
        Returns:
            Formatted captions with line breaks
        """
        formatted_captions = []
        
        for caption in captions:
            text = caption["text"]
            words = text.split()
            
            # Split text into lines
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= max_chars_per_line:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Word is too long, split it
                        lines.append(word[:max_chars_per_line])
                        current_line = word[max_chars_per_line:]
            
            if current_line:
                lines.append(current_line)
            
            # Limit to max_lines
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                if len(lines) == max_lines:
                    lines[-1] = lines[-1][:max_chars_per_line-3] + "..."
            
            formatted_text = "\n".join(lines)
            
            formatted_caption = caption.copy()
            formatted_caption["formatted_text"] = formatted_text
            formatted_caption["lines"] = lines
            formatted_captions.append(formatted_caption)
        
        return formatted_captions
    
    def save_captions(self, captions: List[Dict], output_path: str, format_type: str = "json"):
        """
        Save captions to file in various formats
        
        Args:
            captions: List of caption segments
            output_path: Output file path
            format_type: Output format (json, srt, vtt, txt)
        """
        try:
            if format_type.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(captions, f, ensure_ascii=False, indent=2)
            
            elif format_type.lower() == "srt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for i, caption in enumerate(captions, 1):
                        start_time = self._seconds_to_srt_time(caption["start"])
                        end_time = self._seconds_to_srt_time(caption["end"])
                        text = caption.get("formatted_text", caption["text"])
                        
                        f.write(f"{i}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{text}\n\n")
            
            elif format_type.lower() == "vtt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("WEBVTT\n\n")
                    for caption in captions:
                        start_time = self._seconds_to_vtt_time(caption["start"])
                        end_time = self._seconds_to_vtt_time(caption["end"])
                        text = caption.get("formatted_text", caption["text"])
                        
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{text}\n\n")
            
            elif format_type.lower() == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for caption in captions:
                        f.write(f"[{caption['start']:.2f}s - {caption['end']:.2f}s] {caption['text']}\n")
            
            logger.info(f"Captions saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save captions: {e}")
            raise
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to VTT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def generate_captions_from_audio(
        self, 
        audio_path: str, 
        output_dir: Optional[str] = None,
        save_formats: List[str] = ["json", "srt"]
    ) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Complete pipeline to generate captions from audio file
        
        Args:
            audio_path: Path to audio file
            output_dir: Directory to save caption files
            save_formats: List of formats to save (json, srt, vtt, txt)
            
        Returns:
            Tuple of (captions, output_file_paths)
        """
        if output_dir is None:
            output_dir = os.path.dirname(audio_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate base filename
        base_name = Path(audio_path).stem
        
        # Transcribe audio
        captions = self.transcribe_audio(audio_path)
        
        # Format captions for video
        formatted_captions = self.format_captions_for_video(captions)
        
        # Save in requested formats
        output_paths = {}
        for format_type in save_formats:
            output_path = os.path.join(output_dir, f"{base_name}_captions.{format_type}")
            self.save_captions(formatted_captions, output_path, format_type)
            output_paths[format_type] = output_path
        
        return formatted_captions, output_paths
    
    def generate_captions_from_video(
        self, 
        video_path: str, 
        output_dir: Optional[str] = None,
        save_formats: List[str] = ["json", "srt"],
        cleanup_audio: bool = True
    ) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Complete pipeline to generate captions from video file
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save caption files
            save_formats: List of formats to save (json, srt, vtt, txt)
            cleanup_audio: Whether to delete extracted audio file
            
        Returns:
            Tuple of (captions, output_file_paths)
        """
        # Extract audio from video
        extracted_audio = self.extract_audio_from_video(video_path)
        
        try:
            # Generate captions from extracted audio
            captions, output_paths = self.generate_captions_from_audio(
                extracted_audio, output_dir, save_formats
            )
            
            return captions, output_paths
            
        finally:
            # Cleanup extracted audio file if requested
            if cleanup_audio and os.path.exists(extracted_audio):
                try:
                    os.remove(extracted_audio)
                    logger.info("Cleaned up extracted audio file")
                except Exception as e:
                    logger.warning(f"Failed to cleanup audio file: {e}")


def main():
    """
    Example usage of the HinglishCaptioner
    """
    # Initialize captioner
    captioner = HinglishCaptioner(model_size="medium")
    
    # Example usage - replace with your audio file path
    audio_path = "path/to/your/audio.wav"
    
    if os.path.exists(audio_path):
        try:
            # Generate captions
            captions, output_paths = captioner.generate_captions_from_audio(
                audio_path, 
                output_dir="output/",
                save_formats=["json", "srt", "vtt"]
            )
            
            print(f"Generated {len(captions)} caption segments")
            print("Output files:")
            for format_type, path in output_paths.items():
                print(f"  {format_type.upper()}: {path}")
            
            # Print first few captions
            print("\nFirst 3 captions:")
            for i, caption in enumerate(captions[:3]):
                print(f"  {i+1}. [{caption['start']:.2f}s - {caption['end']:.2f}s] {caption['text']}")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Audio file not found. Please provide a valid audio file path.")


if __name__ == "__main__":
    main()
