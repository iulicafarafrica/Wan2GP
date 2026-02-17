# Wan2GP Audio Studio

A comprehensive audio processing pipeline for Wan2GP featuring segment-by-segment workflow optimized for RTX 3070 (8GB VRAM).

## Features

### Core Components

- **SwiftF0 Integration**: Pitch extraction and manipulation with formant shifting
- **SVC Support**: Multiple voice conversion variants
  - so-vits-svc
  - HQ-SVC
  - Echo
- **Instrumental Generation**: Background music generation and separation
  - HeartMuLa
  - ACE-Step
- **Segment-Based Processing**: Process long audio files in chunks for optimal VRAM usage

### Pipeline Stages

1. **Upload**: Upload audio files (WAV, MP3, FLAC, OGG)
2. **Configuration**: Configure processing parameters
3. **Processing**: Segment-by-segment processing through the pipeline
4. **Preview**: Real-time preview of processed segments
5. **Download**: Download final processed audio

## Architecture

```
audio_studio/
├── audio_frontend/          # React + Tailwind + Wavesurfer.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   └── utils/          # Utility functions
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── audio_backend/           # FastAPI backend
│   ├── main.py            # FastAPI application entry point
│   ├── models/            # Pydantic models and job management
│   ├── pipeline/          # Processing pipeline
│   └── integrations/      # Model wrappers
│       ├── swiftf0_wrapper.py
│       ├── svc_wrapper.py
│       └── instrumental_wrapper.py
└── plugin.py              # Wan2GP integration plugin
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- RTX 3070 or similar GPU with 8GB+ VRAM (recommended)
- CUDA 12.4+

### Installation

1. **Backend Dependencies**

```bash
cd /home/engine/project
source .venv/bin/activate  # or use your virtual environment

# Additional Python dependencies
pip install fastapi uvicorn pydantic
pip install python-multipart
pip install librosa soundfile
pip install torch torchaudio
```

2. **Frontend Dependencies**

```bash
cd audio_frontend
npm install
```

3. **Build Frontend (Optional)**

```bash
cd audio_frontend
npm run build
```

### Running

#### Option 1: Standalone Mode (Recommended for Development)

1. **Start the Backend**

```bash
cd /home/engine/project
source .venv/bin/activate
python audio_backend/main.py
```

The backend will start on `http://127.0.0.1:8001`

2. **Start the Frontend (New Terminal)**

```bash
cd /home/engine/project/audio_frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

3. **Open in Browser**

Navigate to `http://localhost:3000`

#### Option 2: Integrated with Wan2GP

1. **Start Wan2GP normally**

```bash
python wgp.py
```

2. **Navigate to Audio Studio Tab**

The Audio Studio plugin will appear in the main interface. Click on it to see instructions for starting the standalone servers.

### Model Setup (Optional)

The audio processing pipeline includes placeholder wrappers that work without actual model files. To use real models:

#### SwiftF0

```python
# Place model in: models/swiftf0/
# Configure in frontend or API
```

#### SVC Models

```python
# Place models in: models/svc/
# Supported formats: .pth, .pt
```

#### Instrumental Models

```python
# Place models in: models/instrumental/
# HeartMuLa or ACE-Step models
```

## API Documentation

### Endpoints

#### Health Check
```
GET /health
```

#### Upload Audio
```
POST /upload
Content-Type: multipart/form-data
Body: file (audio file)
```

#### Start Job
```
POST /jobs/start
Content-Type: application/json
Body: {
  "config": AudioProcessingConfig,
  "segments": [SegmentDefinition]
}
```

#### Get Job Progress
```
GET /jobs/{job_id}/progress
```

#### Get Job Details
```
GET /jobs/{job_id}
```

#### List Jobs
```
GET /jobs?limit=50&status_filter=running
```

#### Cancel Job
```
DELETE /jobs/{job_id}
```

#### Get Preview
```
GET /jobs/{job_id}/preview?segment_index=0
```

#### Download Result
```
GET /jobs/{job_id}/download
```

#### Model Status
```
GET /models/status
```

#### Load Model
```
POST /models/load/{model_type}?model_path=/path/to/model
```

#### RTX 3070 Profile
```
GET /optimization/rtx3070
```

## Configuration

### RTX 3070 Optimized Settings

```json
{
  "processing": {
    "segment_length": 30.0,
    "overlap_duration": 0.5,
    "max_concurrent_segments": 2,
    "use_gpu": true,
    "clear_cache_between_segments": true
  },
  "quality": {
    "sample_rate": 48000,
    "bit_depth": 16,
    "channels": 2,
    "output_format": "wav"
  }
}
```

### Processing Profiles

**Fast Profile** (Lower quality, faster processing)
- Segment length: 20s
- Sample rate: 44100 Hz
- Max concurrent: 2 segments

**Balanced Profile** (Default)
- Segment length: 30s
- Sample rate: 48000 Hz
- Max concurrent: 2 segments

**Quality Profile** (Higher quality, slower processing)
- Segment length: 30s
- Sample rate: 48000 Hz
- Bit depth: 24
- Max concurrent: 1 segment

## Usage Workflow

1. **Upload Audio**
   - Drag and drop or click to browse
   - Supported formats: WAV, MP3, FLAC, OGG

2. **Configure Processing**
   - Select processing profile (Fast/Balanced/Quality)
   - Configure SwiftF0 settings (pitch shift, formant shift)
   - Configure SVC settings (variant, F0 method, speaker ID)
   - Configure instrumental settings (model, stem separation)
   - Configure audio quality settings

3. **Start Processing**
   - Audio is automatically segmented
   - Each segment is processed through the pipeline
   - Progress is updated in real-time

4. **Preview Results**
   - Preview individual segments
   - Preview combined result
   - Download final output

## Troubleshooting

### Backend Issues

**Backend won't start**
- Check if port 8001 is already in use
- Verify Python dependencies are installed
- Check error logs in terminal

### Frontend Issues

**Frontend won't connect to backend**
- Verify backend is running on http://127.0.0.1:8001
- Check CORS settings in main.py
- Verify API_URL in frontend environment

### Processing Issues

**Out of memory errors**
- Reduce max_concurrent_segments to 1
- Reduce segment_length to 20s
- Clear GPU cache: Add `clear_cache_between_segments: true`

**Slow processing**
- Enable GPU acceleration
- Use "Fast" profile
- Disable unnecessary processing stages

## Development

### Backend Development

```bash
cd audio_backend
python main.py
```

### Frontend Development

```bash
cd audio_frontend
npm run dev
```

### Building for Production

```bash
cd audio_frontend
npm run build
```

The built files will be in `audio_frontend/dist/` and will be served by the FastAPI backend.

## Performance Tips

### RTX 3070 Optimization

1. **Segment Processing**: Use 30-second segments for optimal VRAM usage
2. **Concurrent Segments**: Limit to 2 concurrent segments
3. **Cache Management**: Enable automatic GPU cache clearing
4. **Quality Settings**: 48kHz/16-bit is recommended for best performance/quality balance

### General Optimization

- Use FP16 precision when available
- Enable gradient checkpointing
- Process segments in batches
- Monitor GPU memory usage

## License

This project is part of Wan2GP and follows the same license terms.

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation
- Check Wan2GP documentation
