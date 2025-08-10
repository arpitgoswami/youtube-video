from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from pathlib import Path
import asyncio
import tempfile
from config import config
from image_generator import generate_image
from tts_generator import generate_speech
from video_assembler import assemble_video, add_background_music

app = FastAPI(title="Story Video Creator API")

class Scene(BaseModel):
    prompt: str
    narration: str

class BackgroundMusicRequest(BaseModel):
    video_path: str
    music_path: str
    volume: float = 0.1  # default volume 10%
    output_path: str = "output_with_music.mp4"  # default output filename

class StoryRequest(BaseModel):
    story_scenes: List[Scene]

class StoryResponse(BaseModel):
    message: str
    video_path: str
    total_scenes: int

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
        output_path = "story_video.mp4"
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

@app.post("/add-background-music/", response_model=StoryResponse)
async def add_background_music(request: BackgroundMusicRequest):
    try:
        # Validate input files exist
        if not Path(request.video_path).exists():
            raise HTTPException(status_code=400, detail="Video file not found")
        if not Path(request.music_path).exists():
            raise HTTPException(status_code=400, detail="Music file not found")
            
        # Add background music using positional arguments
        output_path = await asyncio.to_thread(
            add_background_music,
            request.video_path,
            request.music_path,
            request.output_path,
            request.volume  # passing as positional argument
        )
        
        return StoryResponse(
            message="Background music added successfully",
            video_path=output_path,
            total_scenes=1  # Just one video processed
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)