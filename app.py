from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from model import calculate_trending_score

app = FastAPI()

# Mount the 'static' directory to serve index.html and assets
app.mount("/static", StaticFiles(directory="static"), name="static")

class VideoMetadata(BaseModel):
    title: str
    tags: List[str] = []
    description: Optional[str] = ""

@app.post("/trending_score")
async def trending_score(video: VideoMetadata):
    keywords = [video.title] + video.tags
    score = calculate_trending_score(keywords)
    return {"trending_score": score}

@app.get("/")
async def root():
    # Serve the static index.html at root
    return FileResponse("static/index.html")
