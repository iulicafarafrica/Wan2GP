# Wan2GP Audio Studio Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (React + Tailwind CSS)                       │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Upload     │  │   Job Queue  │  │   Progress   │          │
│  │  Handler     │  │   Manager    │  │   Tracker    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌─────────────┐ ┌────────────┐ ┌─────────────┐
│ SwiftF0     │ │   SVC      │ │Instrumental │
│ Wrapper     │ │ Wrapper    │ │  Wrapper    │
└──────┬──────┘ └─────┬──────┘ └──────┬──────┘
       │              │               │
       └──────────────┼───────────────┘
                      ▼
           ┌──────────────────┐
           │  Audio Pipeline   │
           │   Processor     │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │  Segment Manager │
           │ (RTX 3070 Opt.) │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │     Storage     │
           │ (Uploads/Output)│
           └──────────────────┘
```

## Component Details

### Frontend (React + Tailwind + Wavesurfer.js)

**Directory Structure:**
```
audio_frontend/src/
├── components/          # React components
│   ├── AudioUploader.jsx       # File upload with drag-drop
│   ├── WaveSurferPlayer.jsx    # Audio visualization
│   ├── JobProgress.jsx         # Progress tracking
│   └── ConfigForm.jsx          # Configuration UI
├── hooks/               # Custom React hooks
│   ├── useAudioUpload.js       # Upload state management
│   └── useJobManager.js        # Job state & polling
├── services/            # API layer
│   └── api.js                 # Backend API client
├── utils/               # Utilities
│   └── cn.js                  # className merge utility
├── App.jsx              # Main application
├── main.jsx             # Entry point
└── index.css            # Tailwind imports
```

**Key Technologies:**
- **React 18**: UI framework
- **Tailwind CSS**: Styling
- **Wavesurfer.js 7**: Audio waveform visualization
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **Lucide React**: Icons

### Backend (FastAPI)

**Directory Structure:**
```
audio_backend/
├── main.py              # FastAPI application & endpoints
├── models/              # Data models & job management
│   ├── job_manager.py         # Job lifecycle
│   └── audio_config.py        # Pydantic models
├── pipeline/            # Processing pipeline
│   └── processor.py          # Segment processor
├── integrations/        # Model wrappers
│   ├── swiftf0_wrapper.py     # SwiftF0 integration
│   ├── svc_wrapper.py         # SVC integration
│   └── instrumental_wrapper.py # Instrumental integration
└── requirements.txt    # Python dependencies
```

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/models/status` | Model availability |
| POST | `/upload` | Upload audio file |
| POST | `/jobs/start` | Start processing job |
| GET | `/jobs/{id}/progress` | Get job progress |
| GET | `/jobs/{id}` | Get job details |
| GET | `/jobs/{id}/preview` | Get preview audio |
| GET | `/jobs/{id}/download` | Download result |
| DELETE | `/jobs/{id}` | Cancel job |
| POST | `/models/load/{type}` | Load model |

### Data Flow

**Upload Flow:**
```
1. User selects file → Frontend
2. POST /upload → Backend
3. Save to audio_uploads/
4. Return file_id and metadata
5. Update UI with uploaded file info
```

**Processing Flow:**
```
1. User configures settings → Frontend
2. POST /jobs/start → Backend
3. Create job in JobManager
4. Start background task
5. For each segment:
   a. Process through pipeline stages
   b. Update progress
   c. Generate preview
6. Combine segments
7. Mark job complete
8. Frontend polls for progress
```

**Pipeline Stages:**
```
Input Audio
    ↓
[Segmentation] → Split into N segments (30s each)
    ↓
[SwiftF0] → Pitch extraction/manipulation
    ↓
[SVC] → Voice conversion
    ↓
[Instrumental] → Generate/separate instrumental
    ↓
[Mixing] → Combine vocal + instrumental
    ↓
[Combination] → Merge segments
    ↓
Output Audio
```

## RTX 3070 Optimization

### Memory Management

**Segment Strategy:**
- Default segment length: 30 seconds
- Overlap: 0.5 seconds (for smooth transitions)
- Max concurrent: 2 segments
- Automatic GPU cache clearing between segments

**VRAM Usage:**
```
Base Framework: ~2 GB
Segment Processing: ~3-4 GB per segment
Model Loading: ~1-2 GB
Total: ~6-8 GB (fits RTX 3070)
```

### Performance Optimization

**1. Segment Processing:**
```python
# Process in parallel batches
async def process_segments(segments, max_concurrent=2):
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [process_with_limit(seg, semaphore) for seg in segments]
    return await asyncio.gather(*tasks)
```

**2. GPU Cache Management:**
```python
# Clear cache between segments
if config.clear_cache_between_segments:
    torch.cuda.empty_cache()
    gc.collect()
```

**3. Memory Efficient Loading:**
```python
# Load audio segment by segment
for segment in segments:
    audio = load_audio_segment(segment.path, segment.start, segment.end)
    processed = process_audio(audio)
    save_processed(processed)
    del audio, processed  # Free memory immediately
```

### Profile Presets

**Fast Profile:**
- Segment length: 20s
- Concurrent: 2 segments
- Quality: 44.1kHz/16-bit
- VRAM: ~5-6 GB

**Balanced Profile (Default):**
- Segment length: 30s
- Concurrent: 2 segments
- Quality: 48kHz/16-bit
- VRAM: ~6-7 GB

**Quality Profile:**
- Segment length: 30s
- Concurrent: 1 segment
- Quality: 48kHz/24-bit FLAC
- VRAM: ~7-8 GB

## Model Wrappers

### SwiftF0 Wrapper

**Responsibilities:**
- Pitch extraction (F0)
- Pitch shifting
- Formant shifting
- Vibrato preservation

**Placeholder Mode:**
- Uses librosa for basic pitch tracking
- Simple pitch shifting with resampling
- Falls back if model not available

### SVC Wrapper

**Responsibilities:**
- Voice conversion
- Speaker adaptation
- F0 prediction (multiple methods)
- Multi-speaker model support

**Supported Variants:**
- so-vits-svc: Popular, fast
- HQ-SVC: Higher quality
- Echo: Experimental features

**Placeholder Mode:**
- Basic pitch shifting
- No voice conversion
- For testing pipeline only

### Instrumental Wrapper

**Responsibilities:**
- Vocal/instrumental separation
- Stem separation (drums, bass, other)
- Instrumental generation from prompts
- Reverb preservation

**Supported Models:**
- HeartMuLa: High-quality separation
- ACE-Step: Fast separation

**Placeholder Mode:**
- No separation
- Copies input to output
- For testing pipeline only

## Error Handling

**Frontend:**
- Axios interceptors for API errors
- User-friendly error messages
- Retry logic for failed uploads
- Progress indicator resets on error

**Backend:**
- Try-catch blocks around model operations
- Graceful degradation to placeholder mode
- Job status updates on failures
- Detailed error logging

**Recovery:**
- Failed segments marked but processing continues
- User can retry specific segments
- Partial results can be downloaded
- Job can be cancelled mid-processing

## Scalability

**Current Limits:**
- Max file size: 500 MB
- Max segments per job: 100
- Max concurrent jobs: 5
- Job timeout: 1 hour

**Future Improvements:**
- Redis for distributed job queue
- Worker nodes for scaling
- Object storage for large files
- WebSocket for real-time updates

## Security

**Current:**
- CORS configured for localhost
- File type validation
- Path traversal prevention
- Input size limits

**Future:**
- Authentication/authorization
- Rate limiting
- Encrypted storage
- API key management

## Monitoring

**Metrics Tracked:**
- Job success/failure rate
- Average processing time
- GPU memory usage
- API response times

**Logs:**
- Backend: Uvicorn access logs + custom logs
- Frontend: Browser console
- Jobs: Per-job metadata stored
