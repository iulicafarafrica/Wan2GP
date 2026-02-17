# Cover Studio Plugin for Wan2GP

A comprehensive AI-powered full-length cover generation plugin with voice conversion, pitch extraction, and instrumental generation capabilities.

## Features

### Core Functionality
- **Voice Conversion**: Multiple SVC model support (so-vits-svc, HQ-SVC, Echo-SVC)
- **Pitch Extraction**: SwiftF0 for accurate F0 estimation
- **Instrumental Generation**: HeartMuLa/ACE-Step integration (optional)
- **Segment-by-Segment Processing**: Efficiently process long audio files
- **Real-time Waveform Visualization**: Wavesurfer.js powered audio player
- **Modern Web Interface**: React + Tailwind CSS frontend

### Architecture

```
wan2gp-cover-studio/
├── backend/                 # FastAPI server
│   ├── api/                # API endpoints
│   │   └── routes.py       # Upload, process, status endpoints
│   ├── models/             # Model wrappers
│   │   ├── swiftf0.py      # SwiftF0 pitch extractor
│   │   ├── svc_wrapper.py  # SVC voice conversion
│   │   └── instrumental.py # Instrumental generation
│   ├── services/           # Business logic
│   │   └── pipeline.py     # Main processing pipeline
│   ├── utils/              # Utilities
│   │   ├── audio.py        # Audio processing
│   │   └── config.py       # Configuration
│   └── server.py           # FastAPI application
├── frontend/               # React web app
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks (Wavesurfer)
│   │   ├── services/       # API client
│   │   └── App.jsx         # Main application
│   ├── package.json
│   └── tailwind.config.js
├── models/                 # Model storage
│   ├── voice/             # Voice conversion models
│   └── instrumental/      # Instrumental generation models
├── data/                  # Runtime data
│   ├── uploads/          # Uploaded audio files
│   ├── outputs/          # Processed covers
│   └── temp/             # Temporary files
└── plugin.py              # Gradio plugin interface

```

## Installation

### Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.10+
- CUDA-capable GPU (recommended)

### Setup

1. **Plugin Dependencies**
   The plugin will be automatically installed when enabled in Wan2GP. Additional dependencies:
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

2. **Frontend Build** (Optional - for custom development)
   ```bash
   cd plugins/wan2gp-cover-studio/frontend
   npm install
   npm run build
   ```

3. **Model Setup**
   Place your models in the appropriate directories:
   - Voice models: `plugins/wan2gp-cover-studio/models/voice/`
   - Instrumental models: `plugins/wan2gp-cover-studio/models/instrumental/`

## Usage

### Via Gradio Interface

1. Enable the "Cover Studio" plugin in Wan2GP
2. Navigate to the "Cover Studio" tab
3. Click "Start Server"
4. Open the web interface at `http://localhost:8765`

### Web Interface

1. **Upload Audio**: Drag and drop or select an audio file (MP3, WAV, FLAC, OGG, M4A)
2. **Configure Settings**:
   - Select voice conversion model
   - Choose instrumental model (or use original)
   - Adjust pitch shift (-12 to +12 semitones)
   - Enable segment processing for long files
3. **Process**: Click "Start Processing"
4. **Download**: Download the processed cover when complete

### API Endpoints

```
POST   /api/upload                 # Upload audio file
GET    /api/models/voice           # List voice models
GET    /api/models/instrumental    # List instrumental models
POST   /api/process                # Start processing
GET    /api/status/{job_id}        # Get job status
GET    /api/download/{job_id}      # Download result
DELETE /api/job/{job_id}           # Delete job
GET    /api/waveform/{audio_id}    # Get waveform data
GET    /api/health                 # Health check
```

## Pipeline Architecture

### Input Processing
1. Audio file upload and validation
2. Source separation (vocals/instrumental) using librosa HPSS
3. Pitch extraction with SwiftF0

### Voice Conversion
1. Segment audio for efficient processing (optional)
2. Apply SVC model with F0 guidance
3. Pitch shifting as configured

### Instrumental Generation (Optional)
1. Generate instrumental with HeartMuLa/ACE-Step
2. Match duration to converted vocals

### Output
1. Mix converted vocals with instrumental
2. Apply normalization and fading
3. Export as WAV file

## Model Integration

### SwiftF0 (Placeholder)
```python
from models.swiftf0 import SwiftF0Extractor

extractor = SwiftF0Extractor()
f0_curve = extractor.extract_pitch(audio, sample_rate)
```

### SVC Wrapper (Placeholder)
```python
from models.svc_wrapper import SVCWrapper

svc = SVCWrapper()
svc.load_model("path/to/model", model_type="so-vits-svc")
converted = svc.convert_voice(audio, sr, model_id, f0_curve, pitch_shift=2)
```

### Instrumental Generator (Placeholder)
```python
from models.instrumental import InstrumentalGenerator

generator = InstrumentalGenerator()
instrumental = generator.generate(duration=120.0, model="heartmula")
```

## Configuration

### Environment Variables
- `PORT`: Server port (default: 8765)
- `MAX_UPLOAD_SIZE`: Maximum upload size in bytes (default: 100MB)

### Model Configuration
Models are detected automatically from the `models/` directory. The system supports:
- **Voice Models**: `.pth`, `.ckpt` files or model directories
- **Instrumental Models**: Model files or directories

## Development

### Backend Development
```bash
cd plugins/wan2gp-cover-studio/backend
python server.py
```

### Frontend Development
```bash
cd plugins/wan2gp-cover-studio/frontend
npm start
```

### API Testing
```bash
curl http://localhost:8765/api/health
```

## Placeholder Implementations

The current implementation includes placeholder model wrappers that demonstrate the expected interface. To use real models:

1. **SwiftF0**: Integrate the actual SwiftF0 model in `backend/models/swiftf0.py`
2. **SVC**: Add real SVC inference in `backend/models/svc_wrapper.py`
3. **Instrumental**: Implement HeartMuLa/ACE-Step in `backend/models/instrumental.py`

Each wrapper provides the expected interface for the pipeline, making it easy to swap in real implementations.

## Troubleshooting

### Server won't start
- Check if port 8765 is already in use
- Verify FastAPI and uvicorn are installed
- Check logs in Wan2GP console

### Frontend not displaying
- Ensure frontend is built: `cd frontend && npm run build`
- Check browser console for errors
- Verify API endpoint in `frontend/src/services/api.js`

### Processing fails
- Check GPU availability for model inference
- Verify model files are in correct directories
- Check job status via API for error details

## Contributing

To extend the plugin:
1. Add new model wrappers in `backend/models/`
2. Extend the pipeline in `backend/services/pipeline.py`
3. Add UI components in `frontend/src/components/`
4. Update API routes in `backend/api/routes.py`

## License

Part of the Wan2GP project. See main repository for license information.
