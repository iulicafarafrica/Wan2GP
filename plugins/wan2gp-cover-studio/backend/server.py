import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from typing import Optional, List
import json
import uuid
import shutil

from api.routes import router as api_router
from services.pipeline import CoverPipeline
from utils.config import Config

app = FastAPI(title="Cover Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config()
pipeline = CoverPipeline(config)

frontend_dir = Path(__file__).parent.parent / "frontend" / "build"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def read_root():
    if frontend_dir.exists() and (frontend_dir / "index.html").exists():
        return FileResponse(frontend_dir / "index.html")
    
    placeholder_path = Path(__file__).parent / "static_placeholder.html"
    if placeholder_path.exists():
        return FileResponse(placeholder_path)
    
    return {
        "message": "Cover Studio API",
        "version": "1.0.0",
        "frontend": "Not built. Please build the React frontend first.",
        "endpoints": {
            "api_docs": "/docs",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "pipeline": "initialized",
        "models_loaded": pipeline.get_loaded_models()
    }

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if frontend_dir.exists():
        file_path = frontend_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dir / "index.html")
    return {"error": "Frontend not built"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"Starting Cover Studio server on port {port}...")
    print(f"Frontend directory: {frontend_dir}")
    print(f"Frontend exists: {frontend_dir.exists()}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
