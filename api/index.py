from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Story Video Creator API")

class Scene(BaseModel):
    prompt: str
    narration: str

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
            message="Video generation request received",
            status="info"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
