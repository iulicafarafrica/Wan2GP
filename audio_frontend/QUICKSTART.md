# Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- Python 3.10+ installed (for backend)
- Backend server running on port 8001

## Setup

### 1. Install Dependencies (Already Done)
```bash
cd audio_frontend
npm install
```

### 2. Start the Backend
In a separate terminal:
```bash
cd /home/engine/project
python audio_backend/main.py
```

Backend will start on `http://127.0.0.1:8001`

### 3. Start the Frontend
```bash
cd audio_frontend
npm run dev
```

Frontend will start on `http://localhost:3000`

### 4. Open the Application
Open your browser and navigate to:
```
http://localhost:3000
```

## Usage Workflow

### Step 1: Upload Audio
1. Click "Upload" tab
2. Drag and drop an audio file OR click to browse
3. Wait for upload to complete
4. Click "2. Configure" (auto-switches)

### Step 2: Configure Processing
1. Adjust settings in each section:
   - **Processing**: Segment length, concurrent segments
   - **SwiftF0**: Pitch shift, formant shift
   - **SVC**: Voice conversion settings
   - **Instrumental**: Background music settings
   - **Quality**: Sample rate, bit depth, format
2. Use presets: Fast, Balanced, or Quality
3. Click "Start Processing"

### Step 3: Monitor Progress
1. View overall progress (0-100%)
2. See current processing stage
3. Track segment-by-segment progress
4. Wait for completion

### Step 4: Preview & Download
1. Preview the processed audio
2. Download individual segments
3. Download the final result
4. Click "Process Another File" to start over

## Common Issues

### Backend Not Connected
- Ensure backend is running: `python audio_backend/main.py`
- Check backend port (default: 8001)
- Check browser console for errors

### File Upload Fails
- Check file format (WAV, MP3, FLAC, OGG supported)
- Ensure file isn't too large
- Check backend logs for errors

### Waveform Not Showing
- Ensure browser supports Web Audio API
- Try a different browser (Chrome/Firefox recommended)
- Check browser console for errors

### Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Environment Variables

Create `.env` file (optional for development):
```env
VITE_API_URL=http://127.0.0.1:8001
```

Note: In development, the app uses Vite's proxy, so this is optional.

## Tech Stack Reference

- **React 18** - UI framework
- **Vite 6** - Build tool
- **Wavesurfer.js 7** - Audio visualization
- **Tailwind CSS** - Styling
- **React Dropzone** - File upload

## Support

For detailed documentation, see:
- [README.md](./README.md) - Full documentation
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Technical details

## Example API Endpoints

```bash
# Health check
curl http://localhost:8001/health

# Upload file
curl -X POST -F "file=@audio.mp3" http://localhost:8001/upload

# Get model status
curl http://localhost:8001/models/status
```

## Performance Tips

1. **Segment Length**: Use 30-second segments for RTX 3070
2. **Concurrent Segments**: Max 2 for 8GB VRAM
3. **Quality Settings**: Lower quality = faster processing
4. **Batch Processing**: Process multiple files sequentially

## Keyboard Shortcuts

Not currently implemented, but planned for future updates.

## Browser Support

✅ Chrome 90+
✅ Edge 90+
✅ Firefox 88+
✅ Safari 14+

## Next Steps

- Read the full [README.md](./README.md) for detailed documentation
- Check [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) for technical details
- Customize configuration in `vite.config.js` and `tailwind.config.js`
- Add custom components in `src/components/`
- Extend API client in `src/services/api.js`
