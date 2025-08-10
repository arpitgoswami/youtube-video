"""
Video assembly module for the story video maker
"""

import numpy as np
from pathlib import Path
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeAudioClip
from typing import List, Dict
from config import config

def custom_resize_image(image, newsize):
    """Custom resize function using Pillow."""
    if isinstance(image, Image.Image):
        pilim = image
    else:
        pilim = Image.fromarray(image)
    resized_pil = pilim.resize(newsize[::-1], Image.BICUBIC)
    return np.array(resized_pil)

def assemble_video(scene_files: List[Dict], output_file: str, resolution=(1024, 1024), fps=24):
    """Combine scenes into final video."""
    clips = []
    w, h = resolution
    for s in scene_files:
        img_path = str(s["image"])
        audio_path = str(s["audio"])
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        img_clip = ImageClip(img_path).set_duration(duration).set_fps(fps)
        
        # Calculate new width maintaining aspect ratio
        aspect_ratio = img_clip.size[0] / img_clip.size[1]
        new_w = int(h * aspect_ratio)
        img_clip = img_clip.fl_image(lambda pic: custom_resize_image(pic, (new_w, h)))
        
        iw, ih = img_clip.size
        if iw > w:
            x1 = (iw - w) // 2
            img_clip = img_clip.crop(x1=x1, y1=0, x2=x1+w, y2=h)
        elif iw < w:
            img_clip = img_clip.on_color(size=(w, h), color=(0, 0, 0))
            
        img_clip = img_clip.set_audio(audio_clip)
        clips.append(img_clip)
        
    # Add crossfade transitions between clips
    crossfade_duration = config.get("crossfade_duration", 1.0)
    for i in range(len(clips)-1):
        clips[i+1] = clips[i+1].crossfadein(crossfade_duration)
    final = concatenate_videoclips(clips, method="compose")
    
    final.write_videofile(output_file, fps=fps, codec="libx264", audio_codec="aac")

def add_background_music(video_path: str, music_path: str, output_path: str, volume: float = 0.1) -> str:
    """Add background music to an existing video."""
    try:
        # Load video and background music
        video = VideoFileClip(video_path)
        bg_audio = AudioFileClip(music_path)
        
        # Set background music volume
        bg_audio = bg_audio.volumex(volume)
        
        # Loop or trim background music to match video length
        if bg_audio.duration < video.duration:
            bg_audio = bg_audio.loop(duration=video.duration)
        else:
            bg_audio = bg_audio.subclip(0, video.duration)
        
        # Combine original audio with background music
        final_audio = CompositeAudioClip([video.audio, bg_audio])
        final_video = video.set_audio(final_audio)
        
        # Write output file
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        # Close clips
        video.close()
        bg_audio.close()
        final_video.close()
        
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Failed to add background music: {str(e)}")