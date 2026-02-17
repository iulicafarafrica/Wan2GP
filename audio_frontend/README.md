# Wan2GP Audio Studio Frontend

A modern React-based frontend for the Wan2GP Audio Studio audio processing pipeline.

## Features

- **Audio Upload**: Drag-and-drop or click-to-browse file upload with progress tracking
- **Waveform Preview**: Real-time audio visualization using Wavesurfer.js
- **Job Management**: Start, monitor, and cancel processing jobs
- **Progress Tracking**: Real-time progress updates with segment-by-segment visualization
- **Configuration UI**: Comprehensive settings for SwiftF0, SVC, Instrumental generation, and audio quality
- **Result Preview & Download**: Preview processed audio and download final results

## Tech Stack

- **React 18** - UI framework
- **Vite 6** - Build tool and dev server
- **Wavesurfer.js 7** - Audio waveform visualization
- **Tailwind CSS 3** - Styling
- **Axios** - HTTP client (optional, can use fetch)
- **React Dropzone** - File upload handling
- **Lucide React** - Icons

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Wan2GP Audio Studio Backend running on port 8001 (or configured port)

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start development server (runs on port 3000)
npm run dev

# The app will be available at http://localhost:3000
# API requests are proxied to http://127.0.0.1:8001
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory (optional for development):

```env
VITE_API_URL=http://127.0.0.1:8001
```

**Note**: In development mode, the app uses Vite's proxy to forward `/api` requests to the backend, so setting `VITE_API_URL` is optional. In production, set this to your backend API URL.

### Vite Proxy Configuration

The `vite.config.js` is configured to proxy `/api` requests to the backend:

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8001',
      changeOrigin: true,
    },
  },
}
```

Adjust the `target` URL if your backend runs on a different port or host.

## Building for Production

```bash
# Build the application
npm run build

# Preview production build locally
npm run preview
```

The production build will be in the `dist/` directory.

## API Endpoints

The frontend communicates with the following backend endpoints:

- `GET /health` - Health check
- `POST /upload` - Upload audio file
- `POST /jobs/start` - Start processing job
- `GET /jobs/{id}/progress` - Get job progress
- `GET /jobs/{id}` - Get job details
- `GET /jobs/{id}/download` - Download processed audio
- `GET /jobs/{id}/preview` - Get audio preview
- `GET /jobs/{id}/segments` - Get segment information
- `DELETE /jobs/{id}` - Cancel job
- `GET /models/status` - Get model status
- `POST /models/load/{type}` - Load a model

## Workflow

1. **Upload Tab**: Upload an audio file (WAV, MP3, FLAC, OGG)
2. **Configure Tab**: Adjust processing settings (SwiftF0, SVC, Instrumental, Quality)
3. **Progress Tab**: Monitor processing progress in real-time
4. **Preview & Download Tab**: Preview results and download the final audio

## Project Structure

```
audio_frontend/
├── src/
│   ├── components/      # React components
│   │   ├── AudioUploader.jsx
│   │   ├── WaveSurferPlayer.jsx
│   │   ├── JobProgress.jsx
│   │   └── ConfigForm.jsx
│   ├── hooks/          # Custom React hooks
│   │   ├── useAudioUpload.js
│   │   └── useJobManager.js
│   ├── services/       # API service
│   │   └── api.js
│   ├── utils/          # Utility functions
│   │   └── cn.js
│   ├── App.jsx         # Main application component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML entry point
├── vite.config.js      # Vite configuration
├── tailwind.config.js  # Tailwind CSS configuration
└── package.json        # Dependencies and scripts
```

## Styling

The application uses Tailwind CSS with a custom color scheme:

- **Primary**: Sky blue (#0ea5e9)
- **Accent**: Purple (#a855f7)
- **Background**: Dark theme (#111827)
- **Cards**: Gray (#1f2937)

Custom component classes are defined in `index.css` using Tailwind's `@layer` directive.

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Troubleshooting

### Backend Connection Issues

If the frontend can't connect to the backend:

1. Ensure the backend is running: `python audio_backend/main.py`
2. Check the backend port (default: 8001)
3. Update `vite.config.js` proxy target if needed
4. Verify CORS settings in the backend

### Build Errors

If you encounter build errors:

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### WaveSurfer Issues

WaveSurfer requires browser audio support. If you encounter issues:

- Ensure your browser supports Web Audio API
- Check browser console for audio-related errors
- Try a different browser if issues persist

## License

See the main Wan2GP project license.
