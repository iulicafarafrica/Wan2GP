from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, List
from pydantic import BaseModel
import os
import uuid
import shutil
from pathlib import Path

from services.pipeline import CoverPipeline
from utils.config import Config

router = APIRouter()

config = Config()
pipeline = CoverPipeline(config)

class ProcessRequest(BaseModel):
    audio_id: str
    voice_model: str
    instrumental_model: Optional[str] = None
    pitch_shift: int = 0
    use_segments: bool = True
    segment_length: int = 30

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    message: str
    result_url: Optional[str] = None

@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    allowed_extensions = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    audio_id = str(uuid.uuid4())
    upload_dir = config.upload_dir / audio_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"original{file_ext}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        return {
            "audio_id": audio_id,
            "filename": file.filename,
            "size": file_size,
            "format": file_ext[1:],
            "message": "File uploaded successfully"
        }
    except Exception as e:
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/models/voice")
async def list_voice_models():
    return pipeline.list_voice_models()

@router.get("/models/instrumental")
async def list_instrumental_models():
    return pipeline.list_instrumental_models()

@router.post("/process")
async def process_audio(request: ProcessRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    upload_dir = config.upload_dir / request.audio_id
    if not upload_dir.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    background_tasks.add_task(
        pipeline.process_cover,
        job_id=job_id,
        audio_id=request.audio_id,
        voice_model=request.voice_model,
        instrumental_model=request.instrumental_model,
        pitch_shift=request.pitch_shift,
        use_segments=request.use_segments,
        segment_length=request.segment_length
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Processing started"
    }

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    status = pipeline.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status

@router.get("/download/{job_id}")
async def download_result(job_id: str):
    status = pipeline.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    result_path = Path(status["result_path"])
    
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=result_path,
        media_type="audio/wav",
        filename=f"cover_{job_id}.wav"
    )

@router.delete("/job/{job_id}")
async def delete_job(job_id: str):
    success = pipeline.delete_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}

@router.get("/waveform/{audio_id}")
async def get_waveform_data(audio_id: str):
    upload_dir = config.upload_dir / audio_id
    
    if not upload_dir.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    waveform_data = pipeline.generate_waveform_data(audio_id)
    
    return waveform_data
