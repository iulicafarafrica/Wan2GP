from pathlib import Path
import os

class Config:
    def __init__(self):
        self.plugin_dir = Path(__file__).parent.parent.parent
        
        self.upload_dir = self.plugin_dir / "data" / "uploads"
        self.output_dir = self.plugin_dir / "data" / "outputs"
        self.models_dir = self.plugin_dir / "models"
        self.temp_dir = self.plugin_dir / "data" / "temp"
        
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        (self.models_dir / "voice").mkdir(exist_ok=True)
        (self.models_dir / "instrumental").mkdir(exist_ok=True)
        
        self.max_upload_size = int(os.environ.get("MAX_UPLOAD_SIZE", 100 * 1024 * 1024))
        
        self.default_sample_rate = 44100
        self.segment_length = 30
        self.hop_length = 512
        self.n_fft = 2048
        
        print(f"[Config] Plugin directory: {self.plugin_dir}")
        print(f"[Config] Upload directory: {self.upload_dir}")
        print(f"[Config] Output directory: {self.output_dir}")
        print(f"[Config] Models directory: {self.models_dir}")
