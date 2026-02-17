"""
Job Manager for Audio Processing
Handles job lifecycle, status tracking, and result management
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import json

from audio_backend.models.audio_config import AudioProcessingConfig


class JobStatus(Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AudioSegment:
    """Represents a single audio segment for processing"""
    
    def __init__(
        self,
        index: int,
        start_time: float,
        end_time: float,
        original_path: Optional[str] = None
    ):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.original_path = original_path
        self.status = JobStatus.QUEUED
        self.preview_path: Optional[str] = None
        self.result_path: Optional[str] = None
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "index": self.index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "original_path": self.original_path,
            "status": self.status.value,
            "preview_path": self.preview_path,
            "result_path": self.result_path,
            "metadata": self.metadata
        }


class ProcessingJob:
    """Represents a complete audio processing job"""
    
    def __init__(
        self,
        job_id: str,
        config: AudioProcessingConfig,
        segments: List[Dict]
    ):
        self.job_id = job_id
        self.config = config
        self.status = JobStatus.QUEUED
        self.progress = 0.0
        self.current_stage = "initialization"
        self.segments_completed = 0
        self.segments_total = len(segments)
        self.message = "Job created"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results: Dict = {}
        self.preview_url: Optional[str] = None
        
        # Create segment objects
        self.segments: List[AudioSegment] = []
        for idx, seg_data in enumerate(segments):
            segment = AudioSegment(
                index=idx,
                start_time=seg_data.get("start_time", 0.0),
                end_time=seg_data.get("end_time", seg_data.get("start_time", 0.0) + seg_data.get("duration", 10.0)),
                original_path=seg_data.get("original_path")
            )
            self.segments.append(segment)
    
    def update_progress(
        self,
        progress: float,
        current_stage: str,
        message: str
    ):
        """Update job progress"""
        self.progress = progress
        self.current_stage = current_stage
        self.message = message
        self.updated_at = datetime.now()
    
    def update_segment_status(
        self,
        segment_index: int,
        status: JobStatus,
        preview_path: Optional[str] = None,
        result_path: Optional[str] = None
    ):
        """Update status of a specific segment"""
        if 0 <= segment_index < len(self.segments):
            self.segments[segment_index].status = status
            if preview_path:
                self.segments[segment_index].preview_path = preview_path
            if result_path:
                self.segments[segment_index].result_path = result_path
            
            # Update completed count
            self.segments_completed = sum(
                1 for seg in self.segments
                if seg.status in [JobStatus.COMPLETED, JobStatus.FAILED]
            )
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "segments_completed": self.segments_completed,
            "segments_total": self.segments_total,
            "message": self.message,
            "config": self.config.dict(),
            "segments": [seg.to_dict() for seg in self.segments],
            "results": self.results,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "preview_url": self.preview_url
        }


class JobManager:
    """Manages audio processing jobs"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.jobs: Dict[str, ProcessingJob] = {}
        self.storage_dir = storage_dir or Path("./audio_output")
        self.storage_dir.mkdir(exist_ok=True, parents=True)
    
    def create_job(
        self,
        config: AudioProcessingConfig,
        segments: List[Dict]
    ) -> str:
        """
        Create a new processing job
        
        Args:
            config: Audio processing configuration
            segments: List of segment definitions
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = ProcessingJob(job_id, config, segments)
        self.jobs[job_id] = job
        self._save_job_metadata(job)
        return job_id
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """
        Get a job by ID
        
        Args:
            job_id: Job identifier
            
        Returns:
            ProcessingJob or None
        """
        return self.jobs.get(job_id)
    
    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        message: str,
        progress: Optional[float] = None
    ):
        """
        Update job status
        
        Args:
            job_id: Job identifier
            status: New status
            message: Status message
            progress: Optional progress value
        """
        job = self.get_job(job_id)
        if job:
            job.status = status
            job.message = message
            if progress is not None:
                job.progress = progress
            self._save_job_metadata(job)
    
    def update_job_progress(
        self,
        job_id: str,
        progress: float,
        current_stage: str,
        message: str
    ):
        """
        Update job progress
        
        Args:
            job_id: Job identifier
            progress: Progress value (0-100)
            current_stage: Current processing stage
            message: Status message
        """
        job = self.get_job(job_id)
        if job:
            job.update_progress(progress, current_stage, message)
            self._save_job_metadata(job)
    
    def update_segment_status(
        self,
        job_id: str,
        segment_index: int,
        status: JobStatus,
        preview_path: Optional[str] = None,
        result_path: Optional[str] = None
    ):
        """
        Update status of a job segment
        
        Args:
            job_id: Job identifier
            segment_index: Segment index
            status: New status
            preview_path: Optional preview audio path
            result_path: Optional result audio path
        """
        job = self.get_job(job_id)
        if job:
            job.update_segment_status(segment_index, status, preview_path, result_path)
            self._save_job_metadata(job)
    
    def complete_job(self, job_id: str, results: Dict):
        """
        Mark a job as completed
        
        Args:
            job_id: Job identifier
            results: Processing results
        """
        job = self.get_job(job_id)
        if job:
            job.status = JobStatus.COMPLETED
            job.progress = 100.0
            job.current_stage = "completed"
            job.message = "Job completed successfully"
            job.results = results
            job.updated_at = datetime.now()
            self._save_job_metadata(job)
    
    def fail_job(self, job_id: str, error_message: str):
        """
        Mark a job as failed
        
        Args:
            job_id: Job identifier
            error_message: Error description
        """
        job = self.get_job(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.current_stage = "failed"
            job.message = f"Job failed: {error_message}"
            job.updated_at = datetime.now()
            self._save_job_metadata(job)
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled, False otherwise
        """
        job = self.get_job(job_id)
        if job and job.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            job.message = "Job cancelled"
            job.updated_at = datetime.now()
            self._save_job_metadata(job)
            return True
        return False
    
    def list_jobs(
        self,
        limit: int = 50,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        List jobs
        
        Args:
            limit: Maximum number of jobs to return
            status_filter: Optional status filter
            
        Returns:
            List of job dictionaries
        """
        jobs = list(self.jobs.values())
        
        # Filter by status
        if status_filter:
            try:
                filter_status = JobStatus(status_filter.lower())
                jobs = [j for j in jobs if j.status == filter_status]
            except ValueError:
                pass
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        # Limit results
        jobs = jobs[:limit]
        
        return [job.to_dict() for job in jobs]
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job and its files
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if deleted, False otherwise
        """
        if job_id in self.jobs:
            # Delete job files
            job = self.jobs[job_id]
            job_dir = self.storage_dir / job_id
            if job_dir.exists():
                import shutil
                shutil.rmtree(job_dir)
            
            # Delete metadata
            metadata_file = self.storage_dir / f"{job_id}_metadata.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            del self.jobs[job_id]
            return True
        return False
    
    def _save_job_metadata(self, job: ProcessingJob):
        """
        Save job metadata to disk
        
        Args:
            job: ProcessingJob to save
        """
        metadata_file = self.storage_dir / f"{job.job_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(job.to_dict(), f, indent=2, default=str)
    
    def load_job_metadata(self, job_id: str) -> Optional[Dict]:
        """
        Load job metadata from disk
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job metadata dictionary or None
        """
        metadata_file = self.storage_dir / f"{job_id}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return None
