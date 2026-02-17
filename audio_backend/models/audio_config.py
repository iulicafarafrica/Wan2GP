"""
Audio Processing Configuration
Pydantic models for audio processing configuration
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class SVCVariant(str, Enum):
    """SVC model variants"""
    SO_VITS_SVC = "so-vits-svc"
    HQ_SVC = "hq-svc"
    ECHO = "echo"


class InstrumentalModel(str, Enum):
    """Instrumental generation models"""
    HEARTMULA = "heartmula"
    ACE_STEP = "ace-step"


class AudioFormat(str, Enum):
    """Audio output formats"""
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    UPLOAD = "upload"
    SEGMENTATION = "segmentation"
    SWIFTF0 = "swiftf0"
    SVC = "svc"
    INSTRUMENTAL = "instrumental"
    MIXING = "mixing"
    MASTERING = "mastering"
    EXPORT = "export"


class SwiftF0Config(BaseModel):
    """SwiftF0 configuration"""
    enabled: bool = True
    pitch_shift: int = Field(0, ge=-24, le=24, description="Pitch shift in semitones")
    formant_shift: float = Field(1.0, ge=0.5, le=2.0, description="Formant shift factor")
    extract_f0_only: bool = False
    preserve_vibrato: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "pitch_shift": 0,
                "formant_shift": 1.0,
                "extract_f0_only": False,
                "preserve_vibrato": True
            }
        }


class SVCConfig(BaseModel):
    """SVC (Singing Voice Conversion) configuration"""
    enabled: bool = True
    variant: SVCVariant = SVCVariant.SO_VITS_SVC
    model_path: Optional[str] = None
    speaker_id: Optional[str] = None
    f0_method: Literal["crepe", "crepe-tiny", "mangio-crepe", "fcpe", "hybrid"] = "fcpe"
    f0_min: int = Field(50, ge=20, le=200, description="Minimum F0 in Hz")
    f0_max: int = Field(1100, ge=200, le=2000, description="Maximum F0 in Hz")
    cluster_infer_ratio: float = Field(0.0, ge=0.0, le=1.0)
    noise_scale: float = Field(0.4, ge=0.0, le=1.0)
    auto_predict_f0: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "variant": "so-vits-svc",
                "model_path": "/path/to/model.pth",
                "speaker_id": "speaker_01",
                "f0_method": "fcpe",
                "f0_min": 50,
                "f0_max": 1100,
                "cluster_infer_ratio": 0.0,
                "noise_scale": 0.4,
                "auto_predict_f0": False
            }
        }


class InstrumentalConfig(BaseModel):
    """Instrumental generation configuration"""
    enabled: bool = True
    model: InstrumentalModel = InstrumentalModel.ACE_STEP
    model_path: Optional[str] = None
    split_vocals: bool = True
    keep_reverb: bool = False
    stem_separation: bool = False
    stems: List[str] = Field(default_factory=lambda: ["vocals", "drums", "bass", "other"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "model": "ace-step",
                "model_path": "/path/to/model.pth",
                "split_vocals": True,
                "keep_reverb": False,
                "stem_separation": False,
                "stems": ["vocals", "drums", "bass", "other"]
            }
        }


class MixingConfig(BaseModel):
    """Audio mixing configuration"""
    enabled: bool = True
    vocal_volume: float = Field(1.0, ge=0.0, le=2.0)
    instrumental_volume: float = Field(1.0, ge=0.0, le=2.0)
    fade_in: float = Field(0.0, ge=0.0, le=5.0, description="Fade in duration in seconds")
    fade_out: float = Field(0.0, ge=0.0, le=5.0, description="Fade out duration in seconds")
    crossfade_segments: bool = True
    crossfade_duration: float = Field(0.5, ge=0.0, le=2.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "vocal_volume": 1.0,
                "instrumental_volume": 1.0,
                "fade_in": 0.0,
                "fade_out": 0.0,
                "crossfade_segments": bool,
                "crossfade_duration": 0.5
            }
        }


class AudioQualityConfig(BaseModel):
    """Audio quality settings"""
    sample_rate: int = Field(48000, ge=22050, le=96000, description="Sample rate in Hz")
    bit_depth: int = Field(16, ge=16, le=32, description="Bit depth")
    channels: int = Field(2, ge=1, le=2, description="Number of audio channels")
    output_format: AudioFormat = AudioFormat.WAV
    
    class Config:
        json_schema_extra = {
            "example": {
                "sample_rate": 48000,
                "bit_depth": 16,
                "channels": 2,
                "output_format": "wav"
            }
        }


class ProcessingConfig(BaseModel):
    """General processing configuration"""
    segment_length: float = Field(30.0, ge=5.0, le=120.0, description="Segment length in seconds")
    overlap_duration: float = Field(0.5, ge=0.0, le=2.0, description="Overlap between segments")
    max_concurrent_segments: int = Field(2, ge=1, le=4, description="Max concurrent segments for RTX 3070")
    use_gpu: bool = True
    device: str = "cuda"
    clear_cache_between_segments: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment_length": 30.0,
                "overlap_duration": 0.5,
                "max_concurrent_segments": 2,
                "use_gpu": True,
                "device": "cuda",
                "clear_cache_between_segments": True
            }
        }


class AudioProcessingConfig(BaseModel):
    """
    Complete audio processing configuration
    Optimized for RTX 3070 segment workflow
    """
    # General processing settings
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    
    # Quality settings
    quality: AudioQualityConfig = Field(default_factory=AudioQualityConfig)
    
    # Pipeline stages
    swiftf0: SwiftF0Config = Field(default_factory=SwiftF0Config)
    svc: SVCConfig = Field(default_factory=SVCConfig)
    instrumental: InstrumentalConfig = Field(default_factory=InstrumentalConfig)
    mixing: MixingConfig = Field(default_factory=MixingConfig)
    
    # Pipeline order (optional, defaults to standard order)
    pipeline_stages: List[str] = Field(
        default_factory=lambda: [
            "swiftf0",
            "svc",
            "instrumental",
            "mixing"
        ]
    )
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "processing": {
                    "segment_length": 30.0,
                    "overlap_duration": 0.5,
                    "max_concurrent_segments": 2,
                    "use_gpu": True,
                    "device": "cuda",
                    "clear_cache_between_segments": True
                },
                "quality": {
                    "sample_rate": 48000,
                    "bit_depth": 16,
                    "channels": 2,
                    "output_format": "wav"
                },
                "swiftf0": {
                    "enabled": True,
                    "pitch_shift": 0,
                    "formant_shift": 1.0,
                    "extract_f0_only": False,
                    "preserve_vibrato": True
                },
                "svc": {
                    "enabled": True,
                    "variant": "so-vits-svc",
                    "model_path": "/path/to/model.pth",
                    "speaker_id": "speaker_01",
                    "f0_method": "fcpe",
                    "f0_min": 50,
                    "f0_max": 1100,
                    "cluster_infer_ratio": 0.0,
                    "noise_scale": 0.4,
                    "auto_predict_f0": False
                },
                "instrumental": {
                    "enabled": True,
                    "model": "ace-step",
                    "model_path": "/path/to/model.pth",
                    "split_vocals": True,
                    "keep_reverb": False,
                    "stem_separation": False,
                    "stems": ["vocals", "drums", "bass", "other"]
                },
                "mixing": {
                    "enabled": True,
                    "vocal_volume": 1.0,
                    "instrumental_volume": 1.0,
                    "fade_in": 0.0,
                    "fade_out": 0.0,
                    "crossfade_segments": True,
                    "crossfade_duration": 0.5
                },
                "pipeline_stages": ["swiftf0", "svc", "instrumental", "mixing"],
                "metadata": {}
            }
        }
    
    @validator('pipeline_stages')
    def validate_pipeline_stages(cls, v):
        """Validate that pipeline stages are valid"""
        valid_stages = ["swiftf0", "svc", "instrumental", "mixing"]
        for stage in v:
            if stage not in valid_stages:
                raise ValueError(f"Invalid pipeline stage: {stage}")
        return v
    
    def get_rtx3070_profile(self) -> "AudioProcessingConfig":
        """
        Get RTX 3070 optimized configuration
        
        Returns:
            Optimized configuration for RTX 3070 (8GB VRAM)
        """
        config = self.copy()
        
        # Optimize for RTX 3070
        config.processing.max_concurrent_segments = 2
        config.processing.segment_length = 30.0
        config.processing.clear_cache_between_segments = True
        
        # Use reasonable quality settings
        config.quality.sample_rate = 48000
        config.quality.bit_depth = 16
        
        return config


# Pre-configured profiles
def get_rtx3070_fast_profile() -> AudioProcessingConfig:
    """Get fast profile for RTX 3070 (lower quality, faster)"""
    return AudioProcessingConfig(
        processing=ProcessingConfig(
            segment_length=20.0,
            max_concurrent_segments=2
        ),
        quality=AudioQualityConfig(
            sample_rate=44100,
            bit_depth=16
        )
    )


def get_rtx3070_quality_profile() -> AudioProcessingConfig:
    """Get quality profile for RTX 3070 (higher quality, slower)"""
    return AudioProcessingConfig(
        processing=ProcessingConfig(
            segment_length=30.0,
            max_concurrent_segments=1
        ),
        quality=AudioQualityConfig(
            sample_rate=48000,
            bit_depth=24,
            output_format=AudioFormat.FLAC
        )
    )
