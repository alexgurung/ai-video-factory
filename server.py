from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles # New import for serving video
import os
import json
import asyncio

# Import your functions
from main import get_top_news, write_script, download_background, generate_audio, create_video_with_captions

app = FastAPI()

# 1. SERVE THE VIDEO FILE
# This allows the browser to access 'final_video.mp4' via a URL
app.mount("/static", StaticFiles(directory="."), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to track progress
render_progress = {"percent": 0}

@app.get("/api/news-draft")
async def get_draft():
    title = get_top_news()
    script = write_script(title)
    return {"title": title, "script": script}

# 2. THE PROGRESS STREAM
@app.get("/api/progress")
async def progress_stream():
    """Streams the progress percentage to the Next.js frontend."""
    async def event_stream():
        while True:
            yield f"data: {json.dumps(render_progress)}\n\n"
            if render_progress["percent"] >= 100:
                break
            await asyncio.sleep(1) # Check every second
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/api/render")
async def render_video(data: dict, background_tasks: BackgroundTasks):
    user_script = data.get("script")
    title = data.get("title")
    # Reset progress for a new render
    render_progress["percent"] = 0
    background_tasks.add_task(run_full_pipeline, title, user_script)
    return {"message": "Rendering started!"}

# 3. UPDATED PIPELINE WITH PROGRESS STEPS
async def run_full_pipeline(title, script):
    try:
        render_progress["percent"] = 10
        await generate_audio(script)
        
        render_progress["percent"] = 30
        download_background(title)
        
        render_progress["percent"] = 50
        # This is the longest step
        create_video_with_captions("voiceover.mp3", "background.mp4")
        
        render_progress["percent"] = 100
    except Exception as e:
        print(f"Error in pipeline: {e}")
        render_progress["percent"] = 0