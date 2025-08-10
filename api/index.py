from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from mangum import Adapter

app = FastAPI(title="Story Video Creator API")

class Scene(BaseModel):
    prompt: str
    narration: str

class BackgroundMusicRequest(BaseModel):
    video_path: str
    music_path: str
    volume: float = 0.1
    output_path: str = "output_with_music.mp4"

class StoryRequest(BaseModel):
    story_scenes: List[Scene]

class StoryResponse(BaseModel):
    message: str
    status: str

@app.get("/")
async def root():
    return {"message": "Story Video Creator API is running"}

@app.post("/generate-video/")
async def generate_video(request: StoryRequest):
    try:
        return StoryResponse(
            message="This endpoint is under maintenance for Vercel deployment",
            status="info"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-background-music/")
async def add_background_music(request: BackgroundMusicRequest):
    try:
        return StoryResponse(
            message="This endpoint is under maintenance for Vercel deployment",
            status="info"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Handler for AWS Lambda/Vercel
handler = Adapter(app)