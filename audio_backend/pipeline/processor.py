"""
Audio Pipeline Processor
Handles segment-by-segment audio processing workflow
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import torch
import torchaudio
import numpy as np
import librosa

from audio_backend.models.job_manager import JobManager, JobStatus
from audio_backend.models.audio_config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class AudioPipelineProcessor:
    """Process audio through the pipeline segment by segment"""
    
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path("./audio_temp")
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
    async def process(
        self,
        job_id: str,
        config: AudioProcessingConfig,
        segments: List[Dict],
        swiftf0_wrapper: Any,
        svc_wrapper: Any,
        instrumental_wrapper: Any,
        job_manager: JobManager
    ) -> Dict:
        """
        Process audio through the complete pipeline
        
        Args:
            job_id: Job identifier
            config: Processing configuration
            segments: List of segment definitions
            swiftf0_wrapper: SwiftF0 wrapper instance
            svc_wrapper: SVC wrapper instance
            instrumental_wrapper: Instrumental wrapper instance
            job_manager: Job manager instance
            
        Returns:
            Processing results
        """
        results = {
            "job_id": job_id,
            "output_path": None,
            "segments": [],
            "metadata": {}
        }
        
        try:
            # Process each segment
            for segment_idx, segment_data in enumerate(segments):
                logger.info(f"Processing segment {segment_idx + 1}/{len(segments)}")
                
                # Update job progress
                segment_progress = (segment_idx / len(segments)) * 100
                job_manager.update_job_progress(
                    job_id,
                    segment_progress,
                    f"processing_segment_{segment_idx}",
                    f"Processing segment {segment_idx + 1}/{len(segments)}"
                )
                
                # Mark segment as running
                job_manager.update_segment_status(
                    job_id,
                    segment_idx,
                    JobStatus.RUNNING
                )
                
                # Process segment through pipeline
                segment_result = await self._process_segment(
                    job_id=job_id,
                    segment_idx=segment_idx,
                    segment_data=segment_data,
                    config=config,
                    swiftf0_wrapper=swiftf0_wrapper,
                    svc_wrapper=svc_wrapper,
                    instrumental_wrapper=instrumental_wrapper
                )
                
                results["segments"].append(segment_result)
                
                # Update segment status to completed
                job_manager.update_segment_status(
                    job_id,
                    segment_idx,
                    JobStatus.COMPLETED,
                    preview_path=segment_result.get("preview_path"),
                    result_path=segment_result.get("output_path")
                )
                
                # Clear GPU cache if enabled
                if config.processing.clear_cache_between_segments:
                    self._clear_gpu_cache()
            
            # Combine segments
            job_manager.update_job_progress(
                job_id,
                90.0,
                "combining_segments",
                "Combining processed segments"
            )
            
            final_output = await self._combine_segments(
                results["segments"],
                config,
                job_id
            )
            
            results["output_path"] = final_output
            
            # Update final progress
            job_manager.update_job_progress(
                job_id,
                100.0,
                "completed",
                "Processing completed successfully"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            raise
    
    async def _process_segment(
        self,
        job_id: str,
        segment_idx: int,
        segment_data: Dict,
        config: AudioProcessingConfig,
        swiftf0_wrapper: Any,
        svc_wrapper: Any,
        instrumental_wrapper: Any
    ) -> Dict:
        """
        Process a single segment through the pipeline
        
        Args:
            job_id: Job identifier
            segment_idx: Segment index
            segment_data: Segment definition
            config: Processing configuration
            swiftf0_wrapper: SwiftF0 wrapper
            svc_wrapper: SVC wrapper
            instrumental_wrapper: Instrumental wrapper
            
        Returns:
            Segment processing result
        """
        result = {
            "segment_idx": segment_idx,
            "start_time": segment_data.get("start_time"),
            "end_time": segment_data.get("end_time"),
            "output_path": None,
            "preview_path": None,
            "stages": {}
        }
        
        # Load original segment
        original_path = segment_data.get("original_path")
        if not original_path or not Path(original_path).exists():
            logger.warning(f"No original path for segment {segment_idx}, using placeholder")
            original_path = None
        
        # Process through pipeline stages
        current_audio = original_path
        stage_progress_base = (segment_idx / 10) * 10  # Base progress for this segment
        
        for stage_idx, stage in enumerate(config.pipeline_stages):
            try:
                logger.info(f"Processing stage: {stage}")
                
                if stage == "swiftf0" and config.swiftf0.enabled:
                    current_audio = await self._process_swiftf0(
                        current_audio,
                        config.swiftf0,
                        swiftf0_wrapper,
                        job_id,
                        segment_idx
                    )
                    result["stages"]["swiftf0"] = {"status": "completed", "output": current_audio}
                
                elif stage == "svc" and config.svc.enabled:
                    current_audio = await self._process_svc(
                        current_audio,
                        config.svc,
                        svc_wrapper,
                        job_id,
                        segment_idx
                    )
                    result["stages"]["svc"] = {"status": "completed", "output": current_audio}
                
                elif stage == "instrumental" and config.instrumental.enabled:
                    current_audio = await self._process_instrumental(
                        current_audio,
                        config.instrumental,
                        instrumental_wrapper,
                        job_id,
                        segment_idx
                    )
                    result["stages"]["instrumental"] = {"status": "completed", "output": current_audio}
                
                elif stage == "mixing" and config.mixing.enabled:
                    # Mixing requires both vocal and instrumental tracks
                    # For now, pass through
                    result["stages"]["mixing"] = {"status": "skipped", "reason": "Requires multiple tracks"}
                
            except Exception as e:
                logger.error(f"Stage {stage} failed: {e}")
                result["stages"][stage] = {"status": "failed", "error": str(e)}
                # Continue with next stage
        
        # Save final segment output
        if current_audio and Path(current_audio).exists():
            segment_output = self.temp_dir / f"{job_id}_segment_{segment_idx}_final.wav"
            
            # Convert/copy to desired format
            self._convert_audio(
                Path(current_audio),
                segment_output,
                config.quality
            )
            
            result["output_path"] = str(segment_output)
            result["preview_path"] = str(segment_output)
        
        return result
    
    async def _process_swiftf0(
        self,
        input_path: Optional[str],
        config: Any,
        wrapper: Any,
        job_id: str,
        segment_idx: int
    ) -> Optional[str]:
        """Process with SwiftF0"""
        if not input_path or not wrapper.is_available():
            logger.warning(f"SwiftF0 not available or no input, skipping")
            return input_path
        
        try:
            # Load model if not loaded
            if not wrapper.is_loaded():
                wrapper.load()
            
            # Process audio
            output_path = self.temp_dir / f"{job_id}_segment_{segment_idx}_swiftf0.wav"
            
            result = wrapper.process(
                input_path=str(input_path),
                output_path=str(output_path),
                pitch_shift=config.pitch_shift,
                formant_shift=config.formant_shift,
                extract_f0_only=config.extract_f0_only
            )
            
            if result:
                return str(output_path)
            return input_path
            
        except Exception as e:
            logger.error(f"SwiftF0 processing failed: {e}")
            return input_path
    
    async def _process_svc(
        self,
        input_path: Optional[str],
        config: Any,
        wrapper: Any,
        job_id: str,
        segment_idx: int
    ) -> Optional[str]:
        """Process with SVC"""
        if not input_path or not wrapper.is_available():
            logger.warning(f"SVC not available or no input, skipping")
            return input_path
        
        try:
            # Load model if not loaded
            if not wrapper.is_loaded():
                wrapper.load(variant=config.variant, model_path=config.model_path)
            
            # Process audio
            output_path = self.temp_dir / f"{job_id}_segment_{segment_idx}_svc.wav"
            
            result = wrapper.process(
                input_path=str(input_path),
                output_path=str(output_path),
                speaker_id=config.speaker_id,
                f0_method=config.f0_method,
                f0_min=config.f0_min,
                f0_max=config.f0_max,
                cluster_infer_ratio=config.cluster_infer_ratio,
                noise_scale=config.noise_scale
            )
            
            if result:
                return str(output_path)
            return input_path
            
        except Exception as e:
            logger.error(f"SVC processing failed: {e}")
            return input_path
    
    async def _process_instrumental(
        self,
        input_path: Optional[str],
        config: Any,
        wrapper: Any,
        job_id: str,
        segment_idx: int
    ) -> Optional[str]:
        """Process with Instrumental generation"""
        if not input_path or not wrapper.is_available():
            logger.warning(f"Instrumental not available or no input, skipping")
            return input_path
        
        try:
            # Load model if not loaded
            if not wrapper.is_loaded():
                wrapper.load(model_path=config.model_path)
            
            # Process audio
            output_path = self.temp_dir / f"{job_id}_segment_{segment_idx}_instrumental.wav"
            
            result = wrapper.process(
                input_path=str(input_path),
                output_path=str(output_path),
                split_vocals=config.split_vocals,
                stem_separation=config.stem_separation,
                stems=config.stems
            )
            
            if result:
                return str(output_path)
            return input_path
            
        except Exception as e:
            logger.error(f"Instrumental processing failed: {e}")
            return input_path
    
    async def _combine_segments(
        self,
        segments: List[Dict],
        config: AudioProcessingConfig,
        job_id: str
    ) -> str:
        """
        Combine processed segments into final output
        
        Args:
            segments: List of segment results
            config: Processing configuration
            job_id: Job identifier
            
        Returns:
            Path to combined output
        """
        import subprocess
        import tempfile
        
        # Filter segments that have output
        valid_segments = [s for s in segments if s.get("output_path")]
        
        if not valid_segments:
            raise ValueError("No valid segments to combine")
        
        output_path = self.temp_dir / f"{job_id}_combined.{config.quality.output_format.value}"
        
        # Create file list for ffmpeg concatenation
        concat_list = self.temp_dir / f"{job_id}_concat_list.txt"
        with open(concat_list, 'w') as f:
            for segment in valid_segments:
                f.write(f"file '{Path(segment['output_path']).absolute()}'\n")
        
        # Use ffmpeg to concatenate
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Clean up concat list
        if concat_list.exists():
            concat_list.unlink()
        
        return str(output_path)
    
    def _convert_audio(
        self,
        input_path: Path,
        output_path: Path,
        quality_config: Any
    ):
        """
        Convert audio to desired quality settings
        
        Args:
            input_path: Input audio path
            output_path: Output audio path
            quality_config: Audio quality configuration
        """
        import subprocess
        
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-ar", str(quality_config.sample_rate),
            "-ac", str(quality_config.channels),
            "-sample_fmt", "s16" if quality_config.bit_depth == 16 else "s32",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _clear_gpu_cache(self):
        """Clear GPU cache to free memory"""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception as e:
            logger.warning(f"Failed to clear GPU cache: {e}")
