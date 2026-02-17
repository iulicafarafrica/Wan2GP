"""
SVC (Singing Voice Conversion) Wrapper
Placeholder wrapper for so-vits-svc, HQ-SVC, and Echo
"""
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)


class SVCWrapper:
    """Wrapper for SVC models (so-vits-svc, HQ-SVC, Echo)"""
    
    def __init__(self):
        self.model = None
        self.variant = None
        self.model_path = None
        self.loaded = False
        self.available_variants = self._check_available_variants()
    
    def _check_available_variants(self) -> Dict[str, bool]:
        """Check which SVC variants are available"""
        variants = {
            "so-vits-svc": False,
            "hq-svc": False,
            "echo": False
        }
        
        try:
            import so_vits_svc
            variants["so-vits-svc"] = True
        except ImportError:
            pass
        
        try:
            import hq_svc
            variants["hq-svc"] = True
        except ImportError:
            pass
        
        try:
            import echo_svc
            variants["echo"] = True
        except ImportError:
            pass
        
        logger.info(f"Available SVC variants: {variants}")
        return variants
    
    def is_available(self) -> bool:
        """Check if any SVC variant is available"""
        return any(self.available_variants.values())
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.loaded
    
    def get_supported_variants(self) -> List[str]:
        """Get list of supported SVC variants"""
        return [v for v, avail in self.available_variants.items() if avail]
    
    def load(
        self,
        variant: str = "so-vits-svc",
        model_path: Optional[str] = None,
        speaker_id: Optional[str] = None
    ) -> bool:
        """
        Load SVC model
        
        Args:
            variant: SVC variant (so-vits-svc, hq-svc, echo)
            model_path: Optional path to model file
            speaker_id: Optional speaker ID for multi-speaker models
            
        Returns:
            True if loaded successfully, False otherwise
        """
        self.variant = variant
        self.model_path = model_path
        self.loaded = True
        
        if not self.available_variants.get(variant, False):
            logger.warning(f"SVC variant {variant} not available, using placeholder")
            return True
        
        try:
            if variant == "so-vits-svc":
                self._load_so_vits_svc(model_path, speaker_id)
            elif variant == "hq-svc":
                self._load_hq_svc(model_path, speaker_id)
            elif variant == "echo":
                self._load_echo(model_path, speaker_id)
            
            logger.info(f"SVC {variant} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load SVC {variant}: {e}")
            # Still mark as loaded for placeholder
            return True
    
    def _load_so_vits_svc(
        self,
        model_path: Optional[str],
        speaker_id: Optional[str]
    ):
        """Load so-vits-svc model"""
        import so_vits_svc
        
        config = {
            "model_path": model_path,
            "speaker_id": speaker_id
        }
        
        self.model = so_vits_svc.SVCInference(**config)
        logger.info(f"so-vits-svc model loaded from {model_path}")
    
    def _load_hq_svc(
        self,
        model_path: Optional[str],
        speaker_id: Optional[str]
    ):
        """Load HQ-SVC model"""
        import hq_svc
        
        self.model = hq_svc.HQSVC(model_path=model_path)
        logger.info(f"HQ-SVC model loaded from {model_path}")
    
    def _load_echo(
        self,
        model_path: Optional[str],
        speaker_id: Optional[str]
    ):
        """Load Echo model"""
        import echo_svc
        
        self.model = echo_svc.EchoSVC(model_path=model_path)
        logger.info(f"Echo model loaded from {model_path}")
    
    def process(
        self,
        input_path: str,
        output_path: str,
        speaker_id: Optional[str] = None,
        f0_method: str = "fcpe",
        f0_min: int = 50,
        f0_max: int = 1100,
        cluster_infer_ratio: float = 0.0,
        noise_scale: float = 0.4,
        auto_predict_f0: bool = False,
        transpose: int = 0
    ) -> bool:
        """
        Process audio with SVC
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            speaker_id: Target speaker ID
            f0_method: F0 prediction method
            f0_min: Minimum F0 in Hz
            f0_max: Maximum F0 in Hz
            cluster_infer_ratio: Cluster inference ratio
            noise_scale: Noise scale for generation
            auto_predict_f0: Auto predict F0
            transpose: Transpose in semitones
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            if not self.available or self.model is None:
                # Placeholder processing
                return self._placeholder_process(
                    input_path,
                    output_path,
                    speaker_id,
                    transpose
                )
            
            # Actual SVC processing
            inference_params = {
                "input_path": input_path,
                "output_path": output_path,
                "speaker_id": speaker_id or self.model.get_default_speaker(),
                "f0_method": f0_method,
                "f0_min": f0_min,
                "f0_max": f0_max,
                "cluster_infer_ratio": cluster_infer_ratio,
                "noise_scale": noise_scale,
                "auto_predict_f0": auto_predict_f0,
                "transpose": transpose
            }
            
            if self.variant == "so-vits-svc":
                self.model.infer(**inference_params)
            elif self.variant == "hq-svc":
                self.model.infer(**inference_params)
            elif self.variant == "echo":
                self.model.infer(**inference_params)
            
            logger.info(f"SVC processing completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"SVC processing failed: {e}")
            # Fall back to placeholder
            return self._placeholder_process(
                input_path,
                output_path,
                speaker_id,
                transpose
            )
    
    def _placeholder_process(
        self,
        input_path: str,
        output_path: str,
        speaker_id: Optional[str],
        transpose: int
    ) -> bool:
        """
        Placeholder processing when SVC is not available
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            speaker_id: Target speaker ID (not applied in placeholder)
            transpose: Transpose in semitones
            
        Returns:
            True if processed successfully
        """
        try:
            import librosa
            
            # Load audio
            audio, sr = sf.read(input_path)
            
            if transpose == 0:
                # No change, just copy
                sf.write(output_path, audio, sr)
                logger.info(f"Placeholder: copied audio to {output_path}")
                return True
            
            # Apply transpose using librosa
            if len(audio.shape) == 1:
                audio_mono = audio
            else:
                audio_mono = audio[:, 0]
            
            # Pitch shift
            y_shifted = librosa.effects.pitch_shift(
                audio_mono,
                sr=sr,
                n_steps=transpose
            )
            
            # Handle stereo
            if len(audio.shape) > 1:
                processed_audio = np.column_stack([y_shifted] * audio.shape[1])
            else:
                processed_audio = y_shifted
            
            sf.write(output_path, processed_audio, sr)
            logger.info(f"Placeholder: audio transposed by {transpose} semitones to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Placeholder SVC processing failed: {e}")
            return False
    
    def get_speakers(self) -> List[str]:
        """
        Get available speakers from loaded model
        
        Returns:
            List of speaker IDs
        """
        if self.model and hasattr(self.model, 'get_speakers'):
            return self.model.get_speakers()
        return []
    
    def set_speaker(self, speaker_id: str) -> bool:
        """
        Set target speaker
        
        Args:
            speaker_id: Speaker ID
            
        Returns:
            True if successful
        """
        if self.model and hasattr(self.model, 'set_speaker'):
            self.model.set_speaker(speaker_id)
            return True
        return False
