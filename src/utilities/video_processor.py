from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
import os

class VideoProcessor:
    def __init__(self):
        pass
    
    def process_video(self, video_files, image_overlays, output_path):
        """
        Process videos by concatenating them and adding image overlays
        
        Args:
            video_files (list): List of video file paths to concatenate
            image_overlays (list): List of image overlay data dictionaries
            output_path (str): Output file path
        """
        try:
            # Load and concatenate video clips
            video_clips = []
            total_duration = 0
            
            print("Loading video files...")
            for video_file in video_files:
                if os.path.exists(video_file):
                    clip = VideoFileClip(video_file)
                    video_clips.append(clip)
                    total_duration += clip.duration
                    print(f"Loaded: {os.path.basename(video_file)} - Duration: {clip.duration:.2f}s")
                else:
                    print(f"Warning: File not found - {video_file}")
            
            if not video_clips:
                raise ValueError("No valid video files found!")
            
            # Concatenate all video clips
            print("Concatenating videos...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Add image overlays if any
            if image_overlays:
                print("Adding image overlays...")
                clips_to_composite = [final_video]
                
                for overlay in image_overlays:
                    if os.path.exists(overlay['image_path']):
                        # Create image clip
                        img_clip = ImageClip(overlay['image_path'])
                        img_clip = img_clip.set_duration(overlay['duration'])
                        img_clip = img_clip.set_start(overlay['start_time'])
                        
                        # Set position based on overlay settings
                        position = self.get_position_coordinates(overlay['position'], final_video.size, img_clip.size)
                        img_clip = img_clip.set_position(position)
                        
                        clips_to_composite.append(img_clip)
                        print(f"Added overlay: {os.path.basename(overlay['image_path'])} at {overlay['start_time']}s for {overlay['duration']}s")
                    else:
                        print(f"Warning: Image file not found - {overlay['image_path']}")
                
                # Composite all clips
                final_video = CompositeVideoClip(clips_to_composite)
            
            # Write the final video
            print(f"Writing output video to: {output_path}")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Close clips to free memory
            for clip in video_clips:
                clip.close()
            final_video.close()
            
            print("Video processing completed successfully!")
            
        except Exception as e:
            print(f"Error during video processing: {str(e)}")
            raise e
    
    def get_position_coordinates(self, position, video_size, image_size):
        """
        Convert position string to coordinates
        
        Args:
            position (str): Position name (center, top-left, etc.)
            video_size (tuple): (width, height) of video
            image_size (tuple): (width, height) of image
            
        Returns:
            tuple or str: Position coordinates or position string
        """
        video_width, video_height = video_size
        img_width, img_height = image_size
        
        positions = {
            'center': 'center',
            'top-left': (0, 0),
            'top-right': (video_width - img_width, 0),
            'bottom-left': (0, video_height - img_height),
            'bottom-right': (video_width - img_width, video_height - img_height)
        }
        
        return positions.get(position, 'center')
    
    def get_video_info(self, video_path):
        """
        Get basic information about a video file
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            dict: Video information
        """
        try:
            clip = VideoFileClip(video_path)
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'filename': os.path.basename(video_path)
            }
            clip.close()
            return info
        except Exception as e:
            return {'error': str(e)}
