from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List
import uuid
from pathlib import Path
import asyncio
import tempfile
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, vfx
from config import config
from image_generator import generate_image
from tts_generator import generate_speech
from video_assembler import assemble_video

app = FastAPI(title="Story Video Creator API")

class Scene(BaseModel):
    prompt: str
    narration: str

class StoryRequest(BaseModel):
    story_scenes: List[Scene]

class StoryResponse(BaseModel):
    message: str
    video_path: str
    total_scenes: int

class BackgroundMusicRequest(BaseModel):
    video_path: str
    background_music_path: str

class BackgroundMusicResponse(BaseModel):
    message: str
    output_path: str

# Create temporary directory for each request
def create_temp_dir():
    tmp_dir = Path(tempfile.gettempdir()) / f"story_video_{uuid.uuid4().hex}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir

@app.post("/generate-video/", response_model=StoryResponse)
async def generate_video(request: StoryRequest):
    try:
        story_scenes = request.story_scenes
        total_scenes = len(story_scenes)
        
        if total_scenes < 2:
            raise HTTPException(status_code=400, detail="At least 2 scenes are required")
        
        # Create temporary directory for this request
        tmp_dir = create_temp_dir()
        scene_files = []
        
        # Process each scene
        for i, scene in enumerate(story_scenes):
            scene_type = "intro" if i == 0 else "outro" if i == total_scenes - 1 else "scene"
            
            # Generate image and speech for each scene
            image_path = tmp_dir / f"scene_{i}.png"
            audio_path = tmp_dir / f"scene_{i}.mp3"
            
            # Generate image
            await asyncio.to_thread(
                generate_image,
                scene.prompt,
                str(image_path)
            )
            
            # Generate speech
            await asyncio.to_thread(
                generate_speech,
                scene.narration,
                str(audio_path)
            )
            
            scene_files.append({
                "image": str(image_path),
                "audio": str(audio_path)
            })
        
        # Assemble final video
        # Use absolute path in project directory for output
        output_path = str(Path.cwd() / config["output_file"])
        await asyncio.to_thread(
            assemble_video,
            scene_files,
            output_path,
            resolution=config["resolution"],
            fps=config["fps"]
        )
        
        return StoryResponse(
            message="Video generated successfully",
            video_path=output_path,
            total_scenes=total_scenes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-background-music/", response_model=BackgroundMusicResponse)
async def add_background_music(request: BackgroundMusicRequest):
    try:
        # Create temporary directory
        tmp_dir = create_temp_dir()
        # Use project directory for output
        output_path = Path.cwd() / "output_video.mp4"

        # Verify input files exist
        if not Path(request.video_path).exists():
            raise HTTPException(status_code=400, detail="Video file not found")
        if not Path(request.background_music_path).exists():
            raise HTTPException(status_code=400, detail="Background music file not found")

        # Process video with background music
        video_clip = VideoFileClip(request.video_path)
        audio_clip = AudioFileClip(request.background_music_path)

        # Match background audio duration to video duration
        video_duration = video_clip.duration
        audio_duration = audio_clip.duration

        if audio_duration < video_duration:
            processed_audio_clip = audio_clip.fx(vfx.loop, duration=video_duration)
        elif audio_duration > video_duration:
            processed_audio_clip = audio_clip.subclip(0, video_duration)
        else:
            processed_audio_clip = audio_clip

        # Adjust background music volume to 20%
        processed_audio_clip = processed_audio_clip.volumex(0.20)

        # Get original audio from video and combine with background
        original_video_audio = video_clip.audio
        if original_video_audio is not None:
            if original_video_audio.duration > processed_audio_clip.duration:
                processed_audio_clip = processed_audio_clip.fx(vfx.loop, duration=original_video_audio.duration)
            elif processed_audio_clip.duration > original_video_audio.duration:
                original_video_audio = original_video_audio.subclip(0, processed_audio_clip.duration)
            final_audio_clip = CompositeAudioClip([original_video_audio, processed_audio_clip])
        else:
            final_audio_clip = processed_audio_clip

        # Set final audio to video and export
        final_video_clip = video_clip.set_audio(final_audio_clip)
        final_video_clip.write_videofile(str(output_path), codec='libx264', audio_codec='aac')

        # Clean up
        video_clip.close()
        audio_clip.close()
        if original_video_audio is not None:
            original_video_audio.close()
        processed_audio_clip.close()
        final_audio_clip.close()
        final_video_clip.close()

        return BackgroundMusicResponse(
            message="Background music added successfully",
            output_path=str(output_path)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)