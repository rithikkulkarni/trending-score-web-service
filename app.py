from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from model import calculate_trending_score

app = FastAPI()

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
def root():
    return {"message": "Go to /static/index.html"}