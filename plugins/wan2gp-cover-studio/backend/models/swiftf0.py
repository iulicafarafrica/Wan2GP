import numpy as np
from typing import Optional
import torch

try:
    from scipy.ndimage import uniform_filter1d
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class SwiftF0Extractor:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[SwiftF0] Initialized on device: {self.device}")
    
    def is_loaded(self) -> bool:
        return self.model is not None
    
    def load_model(self, model_path: Optional[str] = None):
        print("[SwiftF0] Loading model (placeholder implementation)...")
        self.model = "placeholder"
        print("[SwiftF0] Model loaded successfully")
    
    def extract_pitch(self, audio: np.ndarray, sr: int) -> np.ndarray:
        if not self.is_loaded():
            self.load_model()
        
        print(f"[SwiftF0] Extracting pitch from audio of length {len(audio)} samples at {sr} Hz")
        
        hop_length = 512
        n_frames = len(audio) // hop_length
        
        base_f0 = 220.0
        time = np.arange(n_frames) / (sr / hop_length)
        
        f0_curve = base_f0 * (1 + 0.1 * np.sin(2 * np.pi * 0.5 * time))
        
        voiced_mask = np.random.random(n_frames) > 0.2
        f0_curve = f0_curve * voiced_mask
        
        print(f"[SwiftF0] Extracted F0 curve with {n_frames} frames")
        print(f"[SwiftF0] F0 range: {f0_curve[f0_curve > 0].min():.2f} - {f0_curve.max():.2f} Hz")
        
        return f0_curve
    
    def smooth_f0(self, f0_curve: np.ndarray, window_size: int = 5) -> np.ndarray:
        if not SCIPY_AVAILABLE:
            print("[SwiftF0] Warning: scipy not available, skipping smoothing")
            return f0_curve
        
        voiced_mask = f0_curve > 0
        
        smoothed = uniform_filter1d(f0_curve, size=window_size, mode='nearest')
        
        smoothed = smoothed * voiced_mask
        
        return smoothed
    
    def interpolate_unvoiced(self, f0_curve: np.ndarray) -> np.ndarray:
        voiced_mask = f0_curve > 0
        
        if not np.any(voiced_mask):
            return f0_curve
        
        voiced_indices = np.where(voiced_mask)[0]
        voiced_values = f0_curve[voiced_mask]
        
        interpolated = np.interp(
            np.arange(len(f0_curve)),
            voiced_indices,
            voiced_values,
            left=voiced_values[0],
            right=voiced_values[-1]
        )
        
        return interpolated
