"""
Audio Backend Models
"""
from audio_backend.models.job_manager import (
    JobManager,
    ProcessingJob,
    AudioSegment,
    JobStatus
)
from audio_backend.models.audio_config import (
    AudioProcessingConfig,
    SwiftF0Config,
    SVCConfig,
    InstrumentalConfig,
    MixingConfig,
    AudioQualityConfig,
    ProcessingConfig,
    SVCVariant,
    InstrumentalModel,
    AudioFormat,
    ProcessingStage,
    get_rtx3070_fast_profile,
    get_rtx3070_quality_profile
)

__all__ = [
    "JobManager",
    "ProcessingJob",
    "AudioSegment",
    "JobStatus",
    "AudioProcessingConfig",
    "SwiftF0Config",
    "SVCConfig",
    "InstrumentalConfig",
    "MixingConfig",
    "AudioQualityConfig",
    "ProcessingConfig",
    "SVCVariant",
    "InstrumentalModel",
    "AudioFormat",
    "ProcessingStage",
    "get_rtx3070_fast_profile",
    "get_rtx3070_quality_profile",
]
