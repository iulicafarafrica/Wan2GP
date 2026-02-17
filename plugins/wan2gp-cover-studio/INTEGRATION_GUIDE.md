# Model Integration Guide for Cover Studio

This guide explains how to integrate real AI models into the Cover Studio plugin, replacing the placeholder implementations.

## Table of Contents
- [SwiftF0 Integration](#swiftf0-integration)
- [SVC Model Integration](#svc-model-integration)
- [Instrumental Generation](#instrumental-generation)
- [Testing Your Integration](#testing-your-integration)

---

## SwiftF0 Integration

### Overview
SwiftF0 is a fast and accurate pitch (F0) extraction model. The placeholder implementation generates synthetic F0 curves.

### File to Modify
`backend/models/swiftf0.py`

### Integration Steps

1. **Install SwiftF0 dependencies**
   ```bash
   pip install torchcrepe  # or the actual SwiftF0 package
   ```

2. **Update the `load_model()` method**
   ```python
   def load_model(self, model_path: Optional[str] = None):
       import torchcrepe  # or actual SwiftF0 import
       
       self.model = torchcrepe.load_model('full')  # or load SwiftF0
       self.model.to(self.device)
       self.model.eval()
       print("[SwiftF0] Model loaded successfully")
   ```

3. **Update the `extract_pitch()` method**
   ```python
   def extract_pitch(self, audio: np.ndarray, sr: int) -> np.ndarray:
       if not self.is_loaded():
           self.load_model()
       
       # Convert to tensor
       audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).to(self.device)
       
       # Extract F0
       with torch.no_grad():
           f0, voiced_flag = self.model(audio_tensor, sr)
       
       # Convert back to numpy
       f0_curve = f0.cpu().numpy().squeeze()
       
       return f0_curve
   ```

### Alternative: CREPE
```python
import torchcrepe

def extract_pitch(self, audio: np.ndarray, sr: int) -> np.ndarray:
    audio_tensor = torch.from_numpy(audio).float().to(self.device)
    
    pitch = torchcrepe.predict(
        audio_tensor,
        sr,
        hop_length=512,
        fmin=50,
        fmax=1000,
        model='full',
        batch_size=512,
        device=self.device
    )
    
    return pitch.cpu().numpy()
```

---

## SVC Model Integration

### Overview
Singing Voice Conversion (SVC) models convert vocal characteristics while preserving linguistic content.

### File to Modify
`backend/models/svc_wrapper.py`

### Supported Model Types
- **so-vits-svc 4.0/4.1**: Popular open-source SVC
- **HQ-SVC**: High-quality variant
- **Echo-SVC**: Alternative implementation

### Integration Steps for so-vits-svc

1. **Install dependencies**
   ```bash
   pip install torch torchvision torchaudio
   pip install fairseq
   pip install pyworld praat-parselmouth
   ```

2. **Update the `load_model()` method**
   ```python
   def load_model(self, model_path: str, model_type: str = "so-vits-svc"):
       from inference.infer_tool import Svc
       
       self.model = Svc(model_path, config_path, device=self.device)
       self.model_type = model_type
       self.current_model_path = model_path
       
       print(f"[SVC] Model loaded: {model_type}")
   ```

3. **Update the `convert_voice()` method**
   ```python
   def convert_voice(
       self,
       audio: np.ndarray,
       sr: int,
       model_id: str,
       f0_curve: np.ndarray,
       pitch_shift: int = 0
   ) -> np.ndarray:
       if not self.is_loaded():
           self.load_model(model_id)
       
       # Prepare audio
       audio_tensor = torch.from_numpy(audio).float().to(self.device)
       f0_tensor = torch.from_numpy(f0_curve).float().to(self.device)
       
       # Apply pitch shift
       if pitch_shift != 0:
           pitch_shift_factor = 2 ** (pitch_shift / 12.0)
           f0_tensor = f0_tensor * pitch_shift_factor
       
       # Inference
       with torch.no_grad():
           converted_audio = self.model.infer(
               audio_tensor,
               f0_tensor,
               speaker_id=0
           )
       
       return converted_audio.cpu().numpy()
   ```

### Model File Structure
```
models/voice/
├── my_voice_model/
│   ├── model.pth
│   ├── config.json
│   └── speaker_info.json
```

---

## Instrumental Generation

### Overview
Generate instrumental backing tracks using HeartMuLa or ACE-Step models.

### File to Modify
`backend/models/instrumental.py`

### Integration Steps for HeartMuLa

1. **Install dependencies**
   ```bash
   pip install audiocraft  # or HeartMuLa package
   ```

2. **Update the `load_model()` method**
   ```python
   def load_model(self, model_path: str, model_type: str = "heartmula"):
       from audiocraft.models import MusicGen
       
       self.model = MusicGen.get_pretrained(model_path)
       self.model.to(self.device)
       self.model_type = model_type
       
       print(f"[Instrumental] Model loaded: {model_type}")
   ```

3. **Update the `generate()` method**
   ```python
   def generate(
       self,
       duration: float,
       model: str,
       prompt: Optional[str] = None,
       temperature: float = 1.0,
       sample_rate: int = 44100
   ) -> np.ndarray:
       if not self.is_loaded():
           self.load_model(model)
       
       # Set generation parameters
       self.model.set_generation_params(
           duration=duration,
           temperature=temperature
       )
       
       # Generate
       descriptions = [prompt] if prompt else ["instrumental music"]
       wav = self.model.generate(descriptions)
       
       # Convert to numpy
       instrumental = wav[0].cpu().numpy()
       
       # Resample if needed
       if sample_rate != 32000:  # MusicGen default
           from scipy.signal import resample
           samples = int(len(instrumental) * sample_rate / 32000)
           instrumental = resample(instrumental, samples)
       
       return instrumental
   ```

---

## Testing Your Integration

### Unit Tests

Create `backend/tests/test_models.py`:

```python
import pytest
import numpy as np
from models.swiftf0 import SwiftF0Extractor
from models.svc_wrapper import SVCWrapper
from models.instrumental import InstrumentalGenerator

def test_swiftf0():
    extractor = SwiftF0Extractor()
    audio = np.random.randn(44100)  # 1 second
    f0 = extractor.extract_pitch(audio, 44100)
    
    assert f0 is not None
    assert len(f0) > 0
    assert np.all(f0 >= 0)

def test_svc_conversion():
    svc = SVCWrapper()
    audio = np.random.randn(44100)
    f0 = np.ones(100) * 220.0
    
    converted = svc.convert_voice(audio, 44100, "test_model", f0, 0)
    
    assert converted is not None
    assert len(converted) > 0

def test_instrumental_generation():
    generator = InstrumentalGenerator()
    instrumental = generator.generate(10.0, "test_model")
    
    assert instrumental is not None
    assert len(instrumental) > 0
```

### Integration Test

Create `backend/tests/test_pipeline.py`:

```python
import pytest
from services.pipeline import CoverPipeline
from utils.config import Config

def test_full_pipeline():
    config = Config()
    pipeline = CoverPipeline(config)
    
    # Test with synthetic audio
    import numpy as np
    audio = np.random.randn(44100 * 5)  # 5 seconds
    
    # Mock job processing
    job_id = "test_job"
    audio_id = "test_audio"
    
    # This should complete without errors
    pipeline.process_cover(
        job_id=job_id,
        audio_id=audio_id,
        voice_model="test",
        pitch_shift=0,
        use_segments=True
    )
```

### Manual Testing

1. **Start the server**
   ```bash
   cd plugins/wan2gp-cover-studio/backend
   python server.py
   ```

2. **Test API endpoints**
   ```bash
   # Health check
   curl http://localhost:8765/api/health
   
   # List models
   curl http://localhost:8765/api/models/voice
   
   # Upload audio
   curl -X POST http://localhost:8765/api/upload \
     -F "file=@test_audio.wav"
   ```

3. **Test via frontend**
   - Build frontend: `cd frontend && npm run build`
   - Open browser: `http://localhost:8765`
   - Upload test audio
   - Process with your integrated models

---

## Performance Optimization

### GPU Memory Management

```python
class SVCWrapper:
    def convert_voice(self, ...):
        try:
            # Your inference code
            result = self.model(...)
        finally:
            # Clear cache after inference
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return result
```

### Batch Processing

```python
def process_segments_batch(self, segments, batch_size=4):
    results = []
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i+batch_size]
        batch_results = self.model.process_batch(batch)
        results.extend(batch_results)
    return results
```

### Model Caching

```python
class SVCWrapper:
    _model_cache = {}
    
    def load_model(self, model_path: str):
        if model_path in self._model_cache:
            self.model = self._model_cache[model_path]
            return
        
        # Load model
        self.model = load_svc_model(model_path)
        self._model_cache[model_path] = self.model
```

---

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce segment length
   - Use model quantization
   - Process in smaller batches

2. **Slow Processing**
   - Enable GPU acceleration
   - Use optimized models (ONNX, TensorRT)
   - Implement model caching

3. **Audio Quality Issues**
   - Adjust F0 smoothing parameters
   - Use higher sample rates
   - Fine-tune model hyperparameters

### Debug Mode

Add logging to track processing:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_pitch(self, audio, sr):
    logger.debug(f"Extracting pitch from {len(audio)} samples at {sr}Hz")
    # ... your code
    logger.debug(f"Extracted F0 range: {f0.min():.2f} - {f0.max():.2f} Hz")
```

---

## Additional Resources

- **so-vits-svc**: https://github.com/svc-develop-team/so-vits-svc
- **CREPE (pitch extraction)**: https://github.com/maxrmorrison/torchcrepe
- **MusicGen**: https://github.com/facebookresearch/audiocraft
- **PyWorld**: https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder

## Support

For questions or issues with model integration, refer to the main Wan2GP repository or create an issue in the plugin repository.
