# Frontend-Backend Integration Guide

## API Integration

The frontend communicates with the FastAPI backend on port 8000. All API calls go through the centralized API client in `src/services/api.js`.

## Endpoint Mapping

### Health & Status

**Frontend**: `audioAPI.getHealth()`
**Backend**: `GET /health`
**Response**:
```json
{
  "status": "healthy",
  "models": {
    "swiftf0": true,
    "svc": true,
    "instrumental": true
  }
}
```

### File Upload

**Frontend**: `audioAPI.uploadAudio(file)`
**Backend**: `POST /upload`
**Request**: FormData with file
**Response**:
```json
{
  "file_id": "uuid",
  "filename": "original.wav",
  "safe_filename": "uuid.wav",
  "file_path": "/path/to/file",
  "file_size": 12345,
  "upload_time": "2024-01-01T00:00:00"
}
```

### Job Management

#### Start Job

**Frontend**: `audioAPI.startJob(config, segments)`
**Backend**: `POST /jobs/start`
**Request**:
```json
{
  "config": {
    "processing": { ... },
    "swiftf0": { ... },
    "svc": { ... },
    "instrumental": { ... },
    "quality": { ... }
  },
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 30.0,
      "original_path": "/path/to/file"
    }
  ]
}
```
**Response**:
```json
{
  "job_id": "uuid",
  "status": "queued",
  "message": "Job started successfully"
}
```

#### Get Job Progress

**Frontend**: `audioAPI.getJobProgress(jobId)`
**Backend**: `GET /jobs/{job_id}/progress`
**Response**:
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": 45.5,
  "current_stage": "svc",
  "segments_completed": 2,
  "segments_total": 5,
  "message": "Processing segment 3 of 5",
  "preview_url": "/path/to/preview.wav"
}
```

**Status values**: `queued`, `running`, `completed`, `failed`, `cancelled`

#### Get Full Job Details

**Frontend**: `audioAPI.getJob(jobId)`
**Backend**: `GET /jobs/{job_id}`
**Response**: Extended job information including config, segments, and results

#### Cancel Job

**Frontend**: `audioAPI.cancelJob(jobId)`
**Backend**: `DELETE /jobs/{job_id}`
**Response**:
```json
{
  "job_id": "uuid",
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

### Preview & Download

#### Get Preview URL

**Frontend**: `audioAPI.getPreviewUrl(jobId, segmentIndex)`
**Backend**: `GET /jobs/{job_id}/preview?segment_index={index}`
**Returns**: URL string for use in audio player

#### Download Result

**Frontend**: `audioAPI.getDownloadUrl(jobId)`
**Backend**: `GET /jobs/{job_id}/download`
**Returns**: URL string for download link

### Model Management

**Frontend**: `audioAPI.getModelStatus()`
**Backend**: `GET /models/status`
**Response**:
```json
{
  "swiftf0": {
    "available": true,
    "loaded": true,
    "model_path": "/path/to/model"
  },
  "svc": {
    "available": true,
    "loaded": false,
    "supported_variants": ["so-vits-svc", "hq-svc"]
  },
  "instrumental": {
    "available": true,
    "loaded": true,
    "supported_models": ["heartmula", "ace-step"]
  }
}
```

## State Flow

### 1. Upload Flow

```
User selects file
  → AudioUploader component
  → useAudioUpload hook
  → audioAPI.uploadAudio()
  → Backend stores file
  → Returns file metadata
  → App.jsx updates uploadedFile state
  → Switches to 'config' tab
```

### 2. Job Start Flow

```
User clicks "Start Processing"
  → App.jsx handleStartProcessing()
  → Creates segments array
  → useJobManager.startJob(config, segments)
  → audioAPI.startJob()
  → Backend creates job
  → Returns job_id
  → App.jsx sets currentJobId
  → Starts polling
  → Switches to 'progress' tab
```

### 3. Progress Polling Flow

```
Job started
  → useJobManager.startPolling(jobId)
  → Polls every 2 seconds
  → audioAPI.getJobProgress()
  → Updates job state
  → JobProgress component renders
  → If status is terminal (completed/failed/cancelled)
    → Stops polling
    → Loads full job details
    → Loads segment information
```

### 4. Download Flow

```
Job completed
  → User clicks "Download"
  → App.jsx handleDownload()
  → audioAPI.getDownloadUrl()
  → Opens download URL in new tab
  → Browser downloads file
```

## Error Handling

### API Errors

The API client includes automatic retry logic:

1. **Network Errors**: Retries up to 3 times with exponential backoff
2. **Server Errors (5xx)**: Retries up to 3 times
3. **Client Errors (4xx)**: No retry, immediate error display
4. **Timeout**: Treated as network error, retried

### Error Display

Errors are shown via the `ErrorNotification` component:
- Slides in from the right
- Auto-dismissible
- Shows error message from backend or generic message
- Can be manually closed

### Error Sources

1. **Backend Offline**: Shown when health check fails
2. **Upload Errors**: Shown in AudioUploader component
3. **Job Errors**: Shown globally when job fails
4. **Network Errors**: Shown with retry information

## CORS Configuration

The backend must have CORS enabled for the frontend to work:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Proxy Configuration

Development mode uses Vite proxy to avoid CORS issues:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

Frontend calls `/api/health` → Proxied to `http://127.0.0.1:8000/health`

## Production Deployment

For production, set the API URL via environment variable:

```env
VITE_API_URL=https://your-backend-domain.com
```

The API client will use this URL in production instead of the proxy.

## Testing Integration

### Manual Testing

1. Start backend: `python audio_backend/main.py`
2. Start frontend: `cd audio_frontend && npm run dev`
3. Open `http://localhost:3000`
4. Check "Backend Online" status
5. Upload a test audio file
6. Configure settings
7. Start job and monitor progress
8. Download result

### Test Checklist

- [ ] Backend status shows "Online"
- [ ] Model status loads correctly
- [ ] File upload works
- [ ] Upload progress shows
- [ ] Configuration form saves settings
- [ ] Job starts successfully
- [ ] Progress updates in real-time
- [ ] Segment status displays
- [ ] Job can be cancelled
- [ ] Preview audio loads
- [ ] Download works
- [ ] Errors display correctly
- [ ] Reset button clears state

## Debugging Tips

### Enable Verbose Logging

In `src/services/api.js`, the request method logs all errors. Check browser console for:
- API request URLs
- Request/response data
- Error details

### Network Tab

Use browser DevTools Network tab to inspect:
- Request headers
- Response bodies
- Status codes
- Timing information

### React DevTools

Install React DevTools to inspect:
- Component state
- Hook values
- Re-render causes

### Backend Logs

Check FastAPI logs for:
- Incoming requests
- Processing errors
- Job status changes

## Common Issues

### "Backend Offline" Error

**Cause**: Backend not running or wrong port
**Solution**: 
1. Check backend is running on port 8000
2. Verify `python audio_backend/main.py` is active
3. Check firewall settings

### Waveform Not Loading

**Cause**: CORS or file path issues
**Solution**:
1. Check CORS is enabled in backend
2. Verify preview files are being created
3. Check file paths in job details

### Job Stuck in "Running"

**Cause**: Backend processing error
**Solution**:
1. Check backend logs for errors
2. Verify GPU is available
3. Check segment processing logic

### Upload Fails

**Cause**: File size or format issues
**Solution**:
1. Check file is supported format
2. Verify backend upload directory exists
3. Check file size limits

## Performance Considerations

### Polling Interval

Default: 2 seconds
- Faster polling = more responsive but more server load
- Adjust in `useJobManager.js` if needed

### Waveform Rendering

Wavesurfer.js settings affect performance:
- `barWidth`: Thinner bars = more detail but slower rendering
- `height`: Larger height = more memory
- `normalize`: Expensive but improves visualization

### Memory Usage

Frontend memory considerations:
- Waveform canvases can be large
- Job history accumulates
- Consider clearing old jobs periodically

## Security Notes

### Production Checklist

- [ ] Set specific CORS origins (not "*")
- [ ] Use HTTPS for API calls
- [ ] Validate file uploads on backend
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Sanitize user inputs
- [ ] Set CSP headers
