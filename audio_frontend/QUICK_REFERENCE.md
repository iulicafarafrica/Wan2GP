# Wan2GP Audio Studio - Quick Reference

## Installation & Startup

```bash
# Install dependencies
cd audio_frontend
npm install

# Start development server
npm run dev

# Or use the automated script (starts both backend and frontend)
cd ..
./start_audio_studio.sh
```

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure Quick Map

```
audio_frontend/
├── src/
│   ├── App.jsx                    → Main application, tab routing, state
│   ├── components/
│   │   ├── AudioUploader.jsx      → Drag & drop upload
│   │   ├── WaveSurferPlayer.jsx   → Audio waveform player
│   │   ├── JobProgress.jsx        → Progress tracking UI
│   │   ├── ConfigForm.jsx         → Settings form
│   │   ├── ErrorNotification.jsx  → Error toast
│   │   └── LoadingSpinner.jsx     → Loading indicator
│   ├── hooks/
│   │   ├── useAudioUpload.js      → Upload state management
│   │   └── useJobManager.js       → Job polling & control
│   ├── services/
│   │   └── api.js                 → API client (retry logic)
│   └── utils/
│       └── cn.js                  → Tailwind utility
├── vite.config.js                 → Port 3000, proxy to 8000
└── package.json                   → Dependencies
```

## Common Tasks

### Adding a New Component

```jsx
import { cn } from '@/utils/cn';

export function MyComponent({ className, ...props }) {
  return (
    <div className={cn('card', className)}>
      {/* Your content */}
    </div>
  );
}
```

### Making an API Call

```javascript
import { audioAPI } from '@/services/api';

// In a component or hook
const data = await audioAPI.getHealth();
```

### Using the Job Manager Hook

```jsx
import { useJobManager } from '@/hooks/useJobManager';

function MyComponent() {
  const { job, progress, status, startJob, cancelJob } = useJobManager(jobId);
  
  return <div>Progress: {progress}%</div>;
}
```

### Adding Error Handling

```jsx
import { useState } from 'react';
import { ErrorNotification } from '@/components/ErrorNotification';

function MyComponent() {
  const [error, setError] = useState(null);
  
  return (
    <>
      <ErrorNotification error={error} onClose={() => setError(null)} />
      {/* Your content */}
    </>
  );
}
```

## Styling Guide

### Using Tailwind Utilities

```jsx
// Basic card
<div className="card">Content</div>

// Button variants
<button className="btn btn-primary">Primary</button>
<button className="btn btn-secondary">Secondary</button>
<button className="btn btn-accent">Accent</button>
<button className="btn btn-danger">Danger</button>

// Input
<input className="input" />

// Label
<label className="label">My Label</label>

// Progress bar
<div className="progress-bar">
  <div className="progress-fill" style={{ width: '50%' }} />
</div>
```

### Custom Classes

```javascript
import { cn } from '@/utils/cn';

// Conditionally apply classes
className={cn(
  'base-class',
  condition && 'conditional-class',
  { 'object-syntax': true }
)}
```

## API Reference

### audioAPI Methods

```javascript
// Health & Status
await audioAPI.getHealth()
await audioAPI.getModelStatus()

// Upload
await audioAPI.uploadAudio(file)

// Jobs
await audioAPI.startJob(config, segments)
await audioAPI.getJobProgress(jobId)
await audioAPI.getJob(jobId)
await audioAPI.getJobSegments(jobId)
await audioAPI.cancelJob(jobId)
await audioAPI.listJobs(limit, statusFilter)

// Media
audioAPI.getPreviewUrl(jobId, segmentIndex?)  // Returns URL string
audioAPI.getDownloadUrl(jobId)                // Returns URL string

// Models
await audioAPI.loadModel(modelType, modelPath?)
await audioAPI.getRTX3070Profile()
```

## State Management Patterns

### App-Level State

```jsx
const [uploadedFile, setUploadedFile] = useState(null);
const [currentJobId, setCurrentJobId] = useState(null);
const [config, setConfig] = useState(defaultConfig);
```

### Hook-Based State

```jsx
const { 
  job,           // Current job object
  progress,      // Progress percentage (0-100)
  status,        // 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  segments,      // Array of segment details
  startJob,      // (config, segments) => Promise<jobId>
  cancelJob,     // (jobId) => Promise<void>
  loadJob,       // (jobId) => Promise<job>
  startPolling,  // (jobId) => void
  stopPolling,   // () => void
  error          // Error message string
} = useJobManager(currentJobId);
```

## Configuration Object

```javascript
const config = {
  processing: {
    segment_length: 30.0,           // seconds
    overlap_duration: 0.5,          // seconds
    max_concurrent_segments: 2,     // number
    use_gpu: true,
    device: 'cuda',
    clear_cache_between_segments: true
  },
  quality: {
    sample_rate: 48000,             // Hz
    bit_depth: 16,                  // bits
    channels: 2,                    // 1 or 2
    output_format: 'wav'            // 'wav' | 'flac' | 'mp3'
  },
  swiftf0: {
    enabled: true,
    pitch_shift: 0,                 // semitones (-24 to 24)
    formant_shift: 1.0,             // ratio (0.5 to 2.0)
    extract_f0_only: false,
    preserve_vibrato: true
  },
  svc: {
    enabled: true,
    variant: 'so-vits-svc',         // 'so-vits-svc' | 'hq-svc' | 'echo'
    f0_method: 'fcpe',              // 'crepe' | 'fcpe' | 'hybrid' etc.
    f0_min: 50,                     // Hz
    f0_max: 1100,                   // Hz
    noise_scale: 0.4                // 0.0 to 1.0
  },
  instrumental: {
    enabled: true,
    model: 'ace-step',              // 'heartmula' | 'ace-step'
    split_vocals: true,
    keep_reverb: false
  },
  mixing: {
    enabled: true,
    vocal_volume: 1.0,              // 0.0 to 2.0
    instrumental_volume: 1.0,       // 0.0 to 2.0
    crossfade_segments: true,
    crossfade_duration: 0.5         // seconds
  }
};
```

## Debugging

### Check Backend Connection

```javascript
// In browser console
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

### Enable Verbose API Logging

API client already logs errors. Check browser console for:
- `API Error (endpoint):` messages
- Network tab for request/response details

### React DevTools

Install React DevTools extension to inspect:
- Component state
- Hook values
- Prop flow

### Common Issues

**"Backend Offline"**
- Backend not running: `python audio_backend/main.py`
- Wrong port: Check backend is on 8000
- Firewall blocking: Check localhost access

**Waveform not loading**
- CORS issue: Check backend CORS config
- Bad URL: Verify preview URL format
- File missing: Check backend creates preview files

**Job stuck "Running"**
- Backend error: Check backend logs
- GPU issue: Verify CUDA available
- Processing crash: Check segment processing

## Development Tips

### Hot Reload

Vite automatically reloads on file changes. Save any file to see updates instantly.

### Component Development

Test components in isolation by temporarily rendering only that component in App.jsx.

### API Mocking

For testing without backend:
```javascript
// In api.js temporarily
async getHealth() {
  return { status: 'healthy' };
}
```

### Style Tweaking

Tailwind provides JIT compilation. Add any utility class and it's generated automatically.

## Build & Deploy

```bash
# Production build
npm run build

# Preview production build
npm run preview

# Output is in dist/
```

## Performance Tips

### Optimize Waveform

```javascript
// In WaveSurferPlayer.jsx
barWidth: 2,    // Thinner = faster
height: 80,     // Smaller = faster
normalize: true // Keep for quality
```

### Reduce Polling Frequency

```javascript
// In useJobManager.js
// Change 2000ms to 5000ms for less frequent updates
setInterval(async () => { ... }, 5000);
```

### Lazy Load Components

```javascript
import { lazy, Suspense } from 'react';
const WaveSurferPlayer = lazy(() => import('./components/WaveSurferPlayer'));
```

## Testing Checklist

- [ ] Backend shows "Online"
- [ ] Upload a test file
- [ ] Progress shows during upload
- [ ] Configuration saves
- [ ] Start job works
- [ ] Progress updates
- [ ] Can cancel job
- [ ] Preview plays
- [ ] Download works
- [ ] Errors display

## Useful Commands

```bash
# Verify setup
./verify_setup.sh

# Check dependencies
npm list

# Update dependencies
npm update

# Clear cache
rm -rf node_modules/.vite

# Reinstall
rm -rf node_modules package-lock.json
npm install

# Check for errors
npm run lint
```

## Resources

- **Vite Docs**: https://vitejs.dev
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Wavesurfer.js**: https://wavesurfer.xyz
- **Lucide Icons**: https://lucide.dev

## Support

Check the following files for detailed information:
- `SETUP.md` - Installation and setup
- `INTEGRATION.md` - API integration details
- `AUDIO_FRONTEND_COMPLETE.md` - Full implementation summary
- `README.md` - Project overview
