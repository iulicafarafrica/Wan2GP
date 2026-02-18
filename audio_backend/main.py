"""
Wan2GP Audio Studio Backend
FastAPI server for audio processing pipeline
"""
import os
import sys
import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from audio_backend.models.job_manager import JobManager, JobStatus
from audio_backend.models.audio_config import AudioProcessingConfig
from audio_backend.pipeline.processor import AudioPipelineProcessor
from audio_backend.integrations.swiftf0_wrapper import SwiftF0Wrapper
from audio_backend.integrations.svc_wrapper import SVCWrapper
from audio_backend.integrations.instrumental_wrapper import InstrumentalWrapper

# Initialize FastAPI app
app = FastAPI(
    title="Wan2GP Audio Studio API",
    description="Audio processing pipeline with segment-by-segment workflow",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
job_manager = JobManager()
pipeline_processor = AudioPipelineProcessor()

# Model wrappers (lazy loaded)
swiftf0_wrapper = SwiftF0Wrapper()
svc_wrapper = SVCWrapper()
instrumental_wrapper = InstrumentalWrapper()

# Configuration
UPLOAD_DIR = PROJECT_ROOT / "audio_uploads"
OUTPUT_DIR = PROJECT_ROOT / "audio_output"
TEMP_DIR = PROJECT_ROOT / "audio_temp"
STATIC_DIR = PROJECT_ROOT / "audio_frontend" / "dist"

# Create directories
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Mount static files for frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ==================== Pydantic Models ====================

class JobCreateRequest(BaseModel):
    config: AudioProcessingConfig
    segments: List[Dict]

class ProgressResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    current_stage: str
    segments_completed: int
    segments_total: int
    message: str
    preview_url: Optional[str] = None

class PreviewRequest(BaseModel):
    job_id: str
    segment_index: int


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Wan2GP Audio Studio",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models": {
            "swiftf0": swiftf0_wrapper.is_available(),
            "svc": svc_wrapper.is_available(),
            "instrumental": instrumental_wrapper.is_available()
        }
    }


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file for processing
    
    Args:
        file: Audio file to upload
        
    Returns:
        File metadata and storage path
    """
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        safe_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get basic file info
        file_size = len(content)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "upload_time": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/jobs/start", response_model=Dict)
async def start_job(request: JobCreateRequest, background_tasks: BackgroundTasks):
    """
    Start an audio processing job
    
    Args:
        request: Job configuration with segments
        
    Returns:
        Job ID and initial status
    """
    try:
        # Create job
        job_id = job_manager.create_job(
            config=request.config,
            segments=request.segments
        )
        
        # Start processing in background
        background_tasks.add_task(
            process_job,
            job_id,
            request.config,
            request.segments
        )
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Job started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start job: {str(e)}")


@app.get("/jobs/{job_id}/progress", response_model=ProgressResponse)
async def get_job_progress(job_id: str):
    """
    Get progress for a specific job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Current job progress and status
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ProgressResponse(
        job_id=job_id,
        status=job.status.value,
        progress=job.progress,
        current_stage=job.current_stage,
        segments_completed=job.segments_completed,
        segments_total=job.segments_total,
        message=job.message,
        preview_url=job.preview_url
    )


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Get full job details
    
    Args:
        job_id: Job identifier
        
    Returns:
        Complete job information
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": job.status.value,
        "progress": job.progress,
        "current_stage": job.current_stage,
        "segments_completed": job.segments_completed,
        "segments_total": job.segments_total,
        "message": job.message,
        "config": job.config,
        "segments": job.segments,
        "results": job.results,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "preview_url": job.preview_url
    }


@app.get("/jobs")
async def list_jobs(limit: int = 50, status_filter: Optional[str] = None):
    """
    List all jobs
    
    Args:
        limit: Maximum number of jobs to return
        status_filter: Filter by status (optional)
        
    Returns:
        List of jobs
    """
    jobs = job_manager.list_jobs(limit=limit, status_filter=status_filter)
    return {
        "jobs": jobs,
        "count": len(jobs)
    }


@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a running job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Cancellation confirmation
    """
    success = job_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
    
    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancelled successfully"
    }


@app.get("/jobs/{job_id}/preview")
async def get_preview(job_id: str, segment_index: Optional[int] = None):
    """
    Get preview audio for a job or specific segment
    
    Args:
        job_id: Job identifier
        segment_index: Optional segment index for specific segment preview
        
    Returns:
        Audio file response
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if segment_index is not None:
        # Get specific segment preview
        if segment_index >= len(job.segments):
            raise HTTPException(status_code=400, detail="Invalid segment index")
        preview_path = job.segments[segment_index].get("preview_path")
    else:
        # Get combined preview
        preview_path = job.preview_url
    
    if not preview_path or not Path(preview_path).exists():
        raise HTTPException(status_code=404, detail="Preview not available")
    
    return FileResponse(
        path=preview_path,
        media_type="audio/wav",
        filename=f"preview_{job_id}.wav"
    )


@app.get("/jobs/{job_id}/download")
async def download_result(job_id: str):
    """
    Download final processed audio
    
    Args:
        job_id: Job identifier
        
    Returns:
        Audio file response
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_path = job.results.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        path=output_path,
        media_type="audio/wav",
        filename=f"result_{job_id}.wav"
    )


@app.get("/jobs/{job_id}/segments")
async def get_job_segments(job_id: str):
    """
    Get segment information for a job
    
    Args:
        job_id: Job identifier
        
    Returns:
        List of segment details
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    segments = []
    for idx, segment in enumerate(job.segments):
        segments.append({
            "index": idx,
            "start_time": segment.get("start_time"),
            "end_time": segment.get("end_time"),
            "duration": segment.get("end_time") - segment.get("start_time"),
            "status": segment.get("status", "pending"),
            "preview_path": segment.get("preview_path"),
            "result_path": segment.get("result_path")
        })
    
    return {"segments": segments}


# ==================== Background Processing ====================

async def process_job(job_id: str, config: AudioProcessingConfig, segments: List[Dict]):
    """
    Process a job in the background
    
    Args:
        job_id: Job identifier
        config: Processing configuration
        segments: List of segments to process
    """
    try:
        # Update job status
        job_manager.update_job_status(job_id, JobStatus.RUNNING, "Starting pipeline")
        
        # Process through pipeline
        results = await pipeline_processor.process(
            job_id=job_id,
            config=config,
            segments=segments,
            swiftf0_wrapper=swiftf0_wrapper,
            svc_wrapper=svc_wrapper,
            instrumental_wrapper=instrumental_wrapper,
            job_manager=job_manager
        )
        
        # Mark as completed
        job_manager.complete_job(job_id, results)
        
    except Exception as e:
        # Mark as failed
        job_manager.fail_job(job_id, str(e))


# ==================== Model Management ====================

@app.get("/models/status")
async def get_model_status():
    """
    Get status of all model integrations
    
    Returns:
        Status of each model wrapper
    """
    return {
        "swiftf0": {
            "available": swiftf0_wrapper.is_available(),
            "loaded": swiftf0_wrapper.is_loaded(),
            "model_path": swiftf0_wrapper.model_path
        },
        "svc": {
            "available": svc_wrapper.is_available(),
            "loaded": svc_wrapper.is_loaded(),
            "supported_variants": svc_wrapper.get_supported_variants()
        },
        "instrumental": {
            "available": instrumental_wrapper.is_available(),
            "loaded": instrumental_wrapper.is_loaded(),
            "supported_models": instrumental_wrapper.get_supported_models()
        }
    }


@app.post("/models/load/{model_type}")
async def load_model(model_type: str, model_path: Optional[str] = None):
    """
    Load a specific model
    
    Args:
        model_type: Type of model (swiftf0, svc, instrumental)
        model_path: Optional path to model
        
    Returns:
        Loading status
    """
    try:
        if model_type == "swiftf0":
            success = swiftf0_wrapper.load(model_path)
        elif model_type == "svc":
            variant = None  # Default variant
            success = svc_wrapper.load(variant=variant, model_path=model_path)
        elif model_type == "instrumental":
            success = instrumental_wrapper.load(model_path=model_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model type: {model_type}")
        
        if success:
            return {"status": "loaded", "model_type": model_type}
        else:
            return {"status": "failed", "model_type": model_type, "message": "Model loading failed"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


# ==================== RTX 3070 Optimization ====================

@app.get("/optimization/rtx3070")
async def get_rtx3070_profile():
    """
    Get RTX 3070 optimized settings
    
    Returns:
        Recommended settings for RTX 3070
    """
    return {
        "gpu_memory": "8GB",
        "recommended_batch_size": 1,
        "recommended_segment_length": 30,
        "max_concurrent_segments": 2,
        "sample_rate": 48000,
        "bit_depth": 16,
        "channels": 2,
        "optimization_tips": [
            "Use segment-by-segment processing for better VRAM management",
            "Enable gradient checkpointing where supported",
            "Use mixed precision (FP16) when available",
            "Clear CUDA cache between segments",
            "Limit concurrent segment processing to 2"
        ]
    }


# ==================== Server Startup ====================

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """
    Start the FastAPI server
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
