# Wan2GP Audio Studio - Setup Guide

Complete setup instructions for Wan2GP Audio Studio with RTX 3070 optimization.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Model Setup](#model-setup)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware

- **GPU**: NVIDIA RTX 3070 or better (8GB+ VRAM recommended)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 20GB free space for models and temporary files

### Software

- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS
- **Python**: 3.10 or 3.11
- **Node.js**: 18.x or 20.x
- **CUDA**: 12.4 or higher (for GPU acceleration)

## Installation

### Step 1: Verify Wan2GP Installation

Ensure Wan2GP is properly installed:

```bash
cd /home/engine/project
python wgp.py --help
```

### Step 2: Install Backend Dependencies

Activate your virtual environment:

```bash
cd /home/engine/project
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

Install required Python packages:

```bash
# FastAPI and web server
pip install fastapi uvicorn python-multipart pydantic

# Audio processing
pip install librosa soundfile pydub

# Torch audio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124

# Optional: Install additional models (uncomment if needed)
# pip install audio-separator
# pip install so-vits-svc
```

### Step 3: Install Frontend Dependencies

Navigate to the frontend directory:

```bash
cd audio_frontend
```

Install Node.js dependencies:

```bash
npm install
```

This will install:
- React 18
- Wavesurfer.js (audio visualization)
- Tailwind CSS
- Vite (build tool)
- Axios (HTTP client)

### Step 4: Build Frontend (Optional)

For production deployment:

```bash
npm run build
```

The built files will be in `audio_frontend/dist/`.

## Configuration

### Environment Variables

Create `.env` file in `audio_frontend/` (optional):

```env
# API URL (default: http://127.0.0.1:8001)
VITE_API_URL=http://127.0.0.1:8001

# Additional configuration
VITE_APP_NAME=Wan2GP Audio Studio
```

### Backend Configuration

Edit `audio_backend/main.py` if needed:

```python
# Server configuration
app = FastAPI(
    title="Wan2GP Audio Studio API",
    description="Audio processing pipeline with segment-by-segment workflow",
    version="1.0.0"
)

# Change host and port if needed
def start_server(host: str = "127.0.0.1", port: int = 8001):
    uvicorn.run(app, host=host, port=port, log_level="info")
```

### Directory Structure

Ensure the following directories exist (they will be created automatically):

```
/home/engine/project/
├── audio_uploads/          # Uploaded audio files
├── audio_output/           # Processed output files
├── audio_temp/             # Temporary processing files
├── audio_frontend/
│   └── dist/              # Built frontend files
└── audio_backend/
    └── models/            # Model wrappers
```

## Running the Application

### Development Mode

#### Terminal 1: Start Backend

```bash
cd /home/engine/project
source .venv/bin/activate
python audio_backend/main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

#### Terminal 2: Start Frontend

```bash
cd /home/engine/project/audio_frontend
npm run dev
```

Expected output:
```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

#### Terminal 3: Start Wan2GP (Optional)

If you want to use the integrated plugin:

```bash
cd /home/engine/project
source .venv/bin/activate
python wgp.py
```

### Production Mode

Build the frontend first:

```bash
cd audio_frontend
npm run build
```

Start the backend (it will serve the built frontend):

```bash
cd /home/engine/project
source .venv/bin/activate
python audio_backend/main.py
```

Access the application at: `http://localhost:8001`

### Verify Installation

1. Open browser to `http://localhost:3000` (development) or `http://localhost:8001` (production)

2. Check backend health:
   ```bash
   curl http://127.0.0.1:8001/health
   ```

3. Check model status:
   ```bash
   curl http://127.0.0.1:8001/models/status
   ```

## Model Setup

### Placeholder Mode

The audio studio works in "placeholder mode" by default - it uses basic audio processing without requiring actual model files. This is sufficient for:
- Testing the pipeline
- Basic pitch shifting
- Audio format conversion
- Workflow verification

### Installing Real Models (Optional)

#### SwiftF0

1. Download SwiftF0 model from official repository
2. Place in `models/swiftf0/` directory
3. Configure path in frontend or API

```python
# Example configuration
swiftf0_config = {
    "model_path": "/path/to/models/swiftf0/model.pt"
}
```

#### SVC Models

1. Choose variant: so-vits-svc, HQ-SVC, or Echo
2. Download model from official repository
3. Place in `models/svc/` directory
4. Configure in frontend

```python
# Example configuration
svc_config = {
    "variant": "so-vits-svc",
    "model_path": "/path/to/models/svc/model.pth",
    "speaker_id": "speaker_01"
}
```

**so-vits-svc Setup**:
```bash
pip install so-vits-svc
# Download model to models/svc/so-vits-svc/
```

**HQ-SVC Setup**:
```bash
pip install hq-svc
# Download model to models/svc/hq-svc/
```

**Echo Setup**:
```bash
pip install echo-svc
# Download model to models/svc/echo/
```

#### Instrumental Models

1. Choose model: HeartMuLa or ACE-Step
2. Download from official repository
3. Place in `models/instrumental/` directory
4. Configure in frontend

```python
# Example configuration
instrumental_config = {
    "model": "ace-step",
    "model_path": "/path/to/models/instrumental/ace-step/model.pth"
}
```

**HeartMuLa Setup**:
```bash
pip install heartmula
# Download model to models/instrumental/heartmula/
```

**ACE-Step Setup**:
```bash
pip install ace-step
# Download model to models/instrumental/ace-step/
```

### Model Verification

Check if models are loaded correctly:

```bash
curl http://127.0.0.1:8001/models/status
```

Response:
```json
{
  "swiftf0": {
    "available": true,
    "loaded": true,
    "model_path": "/path/to/model"
  },
  "svc": {
    "available": true,
    "loaded": true,
    "supported_variants": ["so-vits-svc", "hq-svc", "echo"]
  },
  "instrumental": {
    "available": true,
    "loaded": true,
    "supported_models": ["heartmula", "ace-step"]
  }
}
```

## Troubleshooting

### Backend Issues

**Port Already in Use**

```bash
# Find process using port 8001
lsof -i :8001  # Linux/Mac
netstat -ano | findstr :8001  # Windows

# Kill the process or change port
python audio_backend/main.py --port 8002
```

**CUDA Out of Memory**

Edit configuration to reduce memory usage:
```json
{
  "processing": {
    "segment_length": 20,
    "max_concurrent_segments": 1
  }
}
```

**Import Errors**

```bash
# Reinstall dependencies
pip install --force-reinstall fastapi uvicorn pydantic
pip install --force-reinstall torch torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Frontend Issues

**Vite Dev Server Won't Start**

```bash
cd audio_frontend
rm -rf node_modules package-lock.json
npm install
```

**Can't Connect to Backend**

1. Verify backend is running: `curl http://127.0.0.1:8001/health`
2. Check CORS settings in `audio_backend/main.py`
3. Verify API_URL in frontend

### Processing Issues

**Processing Fails Immediately**

1. Check backend logs for error messages
2. Verify uploaded file format is supported
3. Check if there's enough disk space

**Slow Processing**

1. Enable GPU: Set `use_gpu: true` in config
2. Reduce segment length: Try 20s instead of 30s
3. Reduce concurrent segments: Set to 1 instead of 2
4. Use "Fast" profile

**No Audio Output**

1. Check if processing completed successfully
2. Verify output file was created
3. Check browser console for errors
4. Try downloading the file directly

### Common Error Messages

**"SwiftF0 not available"**
- Normal if model not installed
- System uses placeholder processing instead

**"SVC model not loaded"**
- Model path may be incorrect
- Model file may be corrupted
- Check model format is supported

**"CUDA out of memory"**
- Reduce segment length
- Reduce concurrent segments
- Close other GPU applications
- Restart Python process

**"File upload failed"**
- Check file size (should be < 500MB)
- Verify file format is supported
- Check disk space

## Next Steps

1. **Test with Placeholder Mode**: Upload a file and process it
2. **Install Models**: Follow model setup instructions for your use case
3. **Configure Profiles**: Create custom processing profiles
4. **Integrate with Wan2GP**: Use the plugin for integrated workflow

## Additional Resources

- [Wan2GP Documentation](../README.md)
- [API Documentation](README.md#api-documentation)
- [RTX 3070 Optimization Guide](README.md#rtx-3070-optimized-settings)
