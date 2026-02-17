# Cover Studio - Quick Start Guide

Get started with Cover Studio in minutes!

## Prerequisites

- Wan2GP installed and running
- Python 3.10+ with virtual environment
- (Optional) Node.js 18+ for building the frontend

## Installation

### Step 1: Enable the Plugin

1. Launch Wan2GP
2. Navigate to the **Plugin Manager** tab
3. Find "Cover Studio" in the list
4. Enable the plugin
5. Restart Wan2GP

### Step 2: Install Dependencies

The plugin requires FastAPI and uvicorn. These are included in the plugin's `requirements.txt`:

```bash
cd plugins/wan2gp-cover-studio
pip install -r requirements.txt
```

Or install manually:
```bash
pip install fastapi uvicorn python-multipart
```

### Step 3: (Optional) Build the Frontend

The backend works without building the frontend (it will show a placeholder page). To build the full React interface:

```bash
cd plugins/wan2gp-cover-studio/frontend
npm install
npm run build
```

Or use the build script:
```bash
cd plugins/wan2gp-cover-studio
./build_frontend.sh
```

## Usage

### Starting the Server

1. Open Wan2GP and navigate to the **Cover Studio** tab
2. Click the **"▶️ Start Server"** button
3. Wait for the success message
4. Click the link or visit `http://localhost:8765` in your browser

### Processing Your First Cover

#### Via Web Interface

1. **Upload Audio**
   - Drag and drop an audio file (MP3, WAV, FLAC, OGG, M4A)
   - Or click to browse and select
   - Maximum file size: 100MB

2. **Configure Settings**
   - Select a voice model (placeholder models available by default)
   - Choose instrumental generation (or use original)
   - Adjust pitch shift (-12 to +12 semitones)
   - Enable segment processing for long files

3. **Process**
   - Click **"Start Processing"**
   - Monitor progress in real-time
   - Download when complete

#### Via API

```bash
# Upload audio
curl -X POST http://localhost:8765/api/upload \
  -F "file=@my_song.mp3"

# Response: {"audio_id": "abc123..."}

# Start processing
curl -X POST http://localhost:8765/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "audio_id": "abc123...",
    "voice_model": "placeholder",
    "pitch_shift": 0,
    "use_segments": true,
    "segment_length": 30
  }'

# Response: {"job_id": "xyz789..."}

# Check status
curl http://localhost:8765/api/status/xyz789...

# Download result
curl http://localhost:8765/api/download/xyz789... -o cover.wav
```

## Adding Real Models

The plugin ships with placeholder implementations. To use real AI models:

### Voice Models

1. Download a voice conversion model (so-vits-svc, HQ-SVC, etc.)
2. Place in `plugins/wan2gp-cover-studio/models/voice/`
3. Update `backend/models/svc_wrapper.py` with actual inference code
4. See `INTEGRATION_GUIDE.md` for details

### Pitch Extraction

1. Install SwiftF0 or CREPE:
   ```bash
   pip install torchcrepe
   ```
2. Update `backend/models/swiftf0.py`
3. See `INTEGRATION_GUIDE.md` for details

### Instrumental Generation

1. Install HeartMuLa/ACE-Step or audiocraft:
   ```bash
   pip install audiocraft
   ```
2. Update `backend/models/instrumental.py`
3. See `INTEGRATION_GUIDE.md` for details

## File Structure

```
wan2gp-cover-studio/
├── plugin.py              # Gradio integration
├── backend/
│   ├── server.py          # FastAPI server
│   ├── api/routes.py      # API endpoints
│   ├── models/            # Model wrappers
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── frontend/              # React web app
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── hooks/         # React hooks
│   │   └── services/      # API client
│   └── package.json
├── models/                # Place your models here
│   ├── voice/
│   └── instrumental/
└── data/                  # Generated at runtime
    ├── uploads/
    └── outputs/
```

## Configuration

### Server Port

Change the server port by setting the `PORT` environment variable:

```bash
export PORT=9000
```

Or edit `plugin.py`:
```python
self.server_port = 9000
```

### Upload Limits

Edit `backend/utils/config.py`:
```python
self.max_upload_size = 200 * 1024 * 1024  # 200MB
```

### Segment Length

Adjust in the web interface or via API:
```json
{
  "segment_length": 45  // seconds
}
```

## Troubleshooting

### Server Won't Start

**Check if port is in use:**
```bash
lsof -i :8765
```

**Check logs in Wan2GP console**

**Try a different port:**
```python
self.server_port = 8766  # in plugin.py
```

### Frontend Not Showing

**Option 1: Build the frontend**
```bash
cd frontend && npm install && npm run build
```

**Option 2: Use the API directly**
- The backend works without the frontend
- Access API docs at `http://localhost:8765/docs`

### Processing Fails

**Check model files exist:**
```bash
ls -la plugins/wan2gp-cover-studio/models/voice/
```

**Check GPU availability:**
```python
import torch
print(torch.cuda.is_available())
```

**Check logs for errors:**
- View in Wan2GP console
- Check job status via API

### Audio Quality Issues

**Try different settings:**
- Disable segment processing for short files
- Adjust pitch shift
- Use higher quality source audio

**Improve models:**
- Use real trained models instead of placeholders
- Fine-tune model parameters

## Advanced Usage

### Batch Processing

Process multiple files via API:

```python
import requests

files = ['song1.mp3', 'song2.mp3', 'song3.mp3']
jobs = []

for file in files:
    # Upload
    with open(file, 'rb') as f:
        upload_resp = requests.post(
            'http://localhost:8765/api/upload',
            files={'file': f}
        )
    audio_id = upload_resp.json()['audio_id']
    
    # Process
    process_resp = requests.post(
        'http://localhost:8765/api/process',
        json={
            'audio_id': audio_id,
            'voice_model': 'my_model',
            'pitch_shift': 2,
            'use_segments': True
        }
    )
    jobs.append(process_resp.json()['job_id'])

# Monitor jobs
for job_id in jobs:
    status = requests.get(f'http://localhost:8765/api/status/{job_id}')
    print(status.json())
```

### Custom Preprocessing

Edit `backend/services/pipeline.py` to add custom preprocessing:

```python
def process_cover(self, ...):
    # Load audio
    audio, sr = librosa.load(audio_path)
    
    # Custom preprocessing
    audio = self._apply_custom_filter(audio)
    
    # Continue with pipeline...
```

### Integration with Other Plugins

Cover Studio can be used alongside other Wan2GP plugins:

1. Use video generation plugins to create cover videos
2. Use audio separation plugins for better preprocessing
3. Chain with other audio processing tools

## Performance Tips

1. **Use segments for long audio** - Reduces memory usage
2. **Enable GPU acceleration** - Much faster processing
3. **Use quantized models** - Lower memory footprint
4. **Process in batches** - Better GPU utilization
5. **Cache models** - Avoid reloading between jobs

## Getting Help

- **Documentation**: See `README.md` and `INTEGRATION_GUIDE.md`
- **API Docs**: Visit `http://localhost:8765/docs` when server is running
- **Wan2GP Community**: Check the main repository for support
- **Issues**: Report bugs in the Wan2GP issue tracker

## What's Next?

- Add real AI models (see `INTEGRATION_GUIDE.md`)
- Fine-tune processing parameters
- Build custom preprocessing pipelines
- Integrate with other tools and plugins
- Share your models with the community!

---

**Happy covering! 🎤**
