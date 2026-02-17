import os
import json
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import traceback

from models.swiftf0 import SwiftF0Extractor
from models.svc_wrapper import SVCWrapper
from models.instrumental import InstrumentalGenerator
from utils.audio import AudioProcessor
from utils.config import Config

class CoverPipeline:
    def __init__(self, config: Config):
        self.config = config
        self.jobs: Dict[str, Dict[str, Any]] = {}
        
        self.swiftf0 = SwiftF0Extractor()
        self.svc = SVCWrapper()
        self.instrumental = InstrumentalGenerator()
        self.audio_processor = AudioProcessor()
        
        print("[Pipeline] Initialized Cover Studio pipeline")
    
    def get_loaded_models(self) -> Dict[str, bool]:
        return {
            "swiftf0": self.swiftf0.is_loaded(),
            "svc": self.svc.is_loaded(),
            "instrumental": self.instrumental.is_loaded()
        }
    
    def list_voice_models(self) -> List[Dict[str, str]]:
        models_dir = self.config.models_dir / "voice"
        models = []
        
        if models_dir.exists():
            for model_path in models_dir.iterdir():
                if model_path.is_dir() or model_path.suffix in [".pth", ".ckpt"]:
                    models.append({
                        "id": model_path.stem,
                        "name": model_path.stem.replace("_", " ").title(),
                        "type": self._detect_model_type(model_path),
                        "path": str(model_path)
                    })
        
        if not models:
            models.append({
                "id": "placeholder",
                "name": "Placeholder Voice Model",
                "type": "so-vits-svc",
                "path": "placeholder"
            })
        
        return models
    
    def list_instrumental_models(self) -> List[Dict[str, str]]:
        models_dir = self.config.models_dir / "instrumental"
        models = []
        
        if models_dir.exists():
            for model_path in models_dir.iterdir():
                if model_path.is_dir() or model_path.suffix in [".pth", ".ckpt"]:
                    models.append({
                        "id": model_path.stem,
                        "name": model_path.stem.replace("_", " ").title(),
                        "type": "heartmula",
                        "path": str(model_path)
                    })
        
        if not models:
            models.append({
                "id": "none",
                "name": "None (Use Original Instrumental)",
                "type": "none",
                "path": ""
            })
        
        return models
    
    def _detect_model_type(self, model_path: Path) -> str:
        model_name = model_path.stem.lower()
        if "hqsvc" in model_name or "hq-svc" in model_name:
            return "hq-svc"
        elif "echo" in model_name:
            return "echo-svc"
        else:
            return "so-vits-svc"
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)
    
    def delete_job(self, job_id: str) -> bool:
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if "result_path" in job:
                result_path = Path(job["result_path"])
                if result_path.exists():
                    result_path.unlink()
            del self.jobs[job_id]
            return True
        return False
    
    def process_cover(
        self,
        job_id: str,
        audio_id: str,
        voice_model: str,
        instrumental_model: Optional[str] = None,
        pitch_shift: int = 0,
        use_segments: bool = True,
        segment_length: int = 30
    ):
        self.jobs[job_id] = {
            "status": "processing",
            "progress": 0.0,
            "message": "Starting pipeline...",
            "started_at": datetime.now().isoformat()
        }
        
        try:
            upload_dir = self.config.upload_dir / audio_id
            audio_files = list(upload_dir.glob("original.*"))
            
            if not audio_files:
                raise FileNotFoundError("Original audio file not found")
            
            audio_path = audio_files[0]
            
            self._update_job(job_id, 0.05, "Loading audio file...")
            audio, sr = librosa.load(str(audio_path), sr=None)
            
            self._update_job(job_id, 0.1, "Separating vocals and instrumental...")
            vocals, instrumental = self.audio_processor.separate_vocals(audio, sr)
            
            self._update_job(job_id, 0.2, "Extracting pitch with SwiftF0...")
            f0_curve = self.swiftf0.extract_pitch(vocals, sr)
            
            if use_segments:
                self._update_job(job_id, 0.3, "Segmenting audio...")
                segments = self._create_segments(vocals, sr, segment_length)
                
                self._update_job(job_id, 0.4, f"Processing {len(segments)} segments...")
                processed_segments = []
                
                for i, segment in enumerate(segments):
                    progress = 0.4 + (i / len(segments)) * 0.3
                    self._update_job(job_id, progress, f"Processing segment {i+1}/{len(segments)}...")
                    
                    segment_f0 = f0_curve[segment["start_frame"]:segment["end_frame"]]
                    processed = self.svc.convert_voice(
                        segment["audio"],
                        sr,
                        voice_model,
                        segment_f0,
                        pitch_shift
                    )
                    processed_segments.append(processed)
                
                self._update_job(job_id, 0.7, "Merging segments...")
                vocals_converted = np.concatenate(processed_segments)
            else:
                self._update_job(job_id, 0.4, "Converting voice...")
                vocals_converted = self.svc.convert_voice(
                    vocals,
                    sr,
                    voice_model,
                    f0_curve,
                    pitch_shift
                )
            
            if instrumental_model and instrumental_model != "none":
                self._update_job(job_id, 0.8, "Generating instrumental...")
                instrumental = self.instrumental.generate(
                    duration=len(vocals_converted) / sr,
                    model=instrumental_model
                )
            
            self._update_job(job_id, 0.9, "Mixing final output...")
            final_audio = self.audio_processor.mix_audio(vocals_converted, instrumental, sr)
            
            output_dir = self.config.output_dir / job_id
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "cover.wav"
            
            sf.write(str(output_path), final_audio, sr)
            
            self.jobs[job_id] = {
                "status": "completed",
                "progress": 1.0,
                "message": "Processing completed successfully",
                "result_path": str(output_path),
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[Pipeline] Job {job_id} failed: {error_msg}")
            traceback.print_exc()
            
            self.jobs[job_id] = {
                "status": "failed",
                "progress": 0.0,
                "message": error_msg,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
    
    def _update_job(self, job_id: str, progress: float, message: str):
        if job_id in self.jobs:
            self.jobs[job_id]["progress"] = progress
            self.jobs[job_id]["message"] = message
            print(f"[Pipeline] Job {job_id}: {progress:.1%} - {message}")
    
    def _create_segments(
        self,
        audio: np.ndarray,
        sr: int,
        segment_length: int
    ) -> List[Dict[str, Any]]:
        segment_samples = segment_length * sr
        total_samples = len(audio)
        segments = []
        
        for start_sample in range(0, total_samples, segment_samples):
            end_sample = min(start_sample + segment_samples, total_samples)
            
            segments.append({
                "audio": audio[start_sample:end_sample],
                "start_sample": start_sample,
                "end_sample": end_sample,
                "start_frame": start_sample,
                "end_frame": end_sample,
                "duration": (end_sample - start_sample) / sr
            })
        
        return segments
    
    def generate_waveform_data(self, audio_id: str) -> Dict[str, Any]:
        upload_dir = self.config.upload_dir / audio_id
        audio_files = list(upload_dir.glob("original.*"))
        
        if not audio_files:
            raise FileNotFoundError("Audio file not found")
        
        audio_path = audio_files[0]
        audio, sr = librosa.load(str(audio_path), sr=22050, mono=True)
        
        downsample_factor = 100
        downsampled = audio[::downsample_factor]
        
        return {
            "samples": downsampled.tolist(),
            "sample_rate": sr,
            "duration": len(audio) / sr,
            "channels": 1
        }
