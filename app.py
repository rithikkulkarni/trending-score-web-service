from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from model import calculate_trending_score

app = FastAPI(
    title="Trending Score Calculator",
    description="Enter text to calculate a trending score based on various social media trends.",
    version="1.0.0"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["POST","GET"],
  allow_headers=["*"],
)

# Mount the 'static' directory to serve index.html and assets
app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

class VideoMetadata(BaseModel):
    title: str

@app.post("/trending_score")
async def trending_score(video: VideoMetadata):
    try:
        keywords = [video.title]
        score = calculate_trending_score(keywords)
        return {"trending_score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    # Serve the static index.html at root
    return FileResponse("static/index.html")
