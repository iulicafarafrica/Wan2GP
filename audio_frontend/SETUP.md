# Wan2GP Audio Studio Frontend - Setup Guide

## Overview

This is the React-based frontend for the Wan2GP Audio Studio. It provides a modern, user-friendly interface for audio processing with real-time waveform visualization, job progress tracking, and comprehensive configuration options.

## Features

- **Audio Upload**: Drag & drop interface for uploading audio files (WAV, MP3, FLAC, OGG)
- **Waveform Preview**: Real-time waveform visualization using Wavesurfer.js
- **Job Management**: Start, monitor, and cancel audio processing jobs
- **Progress Tracking**: Real-time progress updates with segment-level details
- **Configuration**: Comprehensive settings for processing, quality, and effects
- **Download**: Download processed audio files
- **Error Handling**: Robust error notifications and retry logic
- **RTX 3070 Optimized**: Pre-configured settings for optimal 8GB VRAM usage

## Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
```bash
cd audio_frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Frontend

### Development Mode

Start the development server with hot-reload:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

Build the application for production:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Configuration

### Environment Variables

Create a `.env` file in the `audio_frontend` directory:

```env
VITE_API_URL=http://127.0.0.1:8000
```

### Vite Proxy

The Vite development server is configured to proxy API requests from `/api/*` to `http://127.0.0.1:8000`. This is configured in `vite.config.js`.

## Backend Connection

The frontend expects the FastAPI backend to be running on port 8000. Key endpoints:

- `GET /health` - Health check
- `POST /upload` - Upload audio file
- `POST /jobs/start` - Start processing job
- `GET /jobs/{job_id}/progress` - Get job progress
- `GET /jobs/{job_id}/download` - Download result
- `GET /jobs/{job_id}/preview` - Preview audio

## Project Structure

```
audio_frontend/
├── src/
│   ├── components/
│   │   ├── AudioUploader.jsx       # File upload with drag & drop
│   │   ├── WaveSurferPlayer.jsx    # Waveform player
│   │   ├── JobProgress.jsx         # Job progress display
│   │   ├── ConfigForm.jsx          # Configuration form
│   │   ├── ErrorNotification.jsx   # Error notifications
│   │   └── LoadingSpinner.jsx      # Loading indicator
│   ├── hooks/
│   │   ├── useAudioUpload.js       # Upload management hook
│   │   └── useJobManager.js        # Job polling and state hook
│   ├── services/
│   │   └── api.js                  # API client with retry logic
│   ├── utils/
│   │   └── cn.js                   # Tailwind class utility
│   ├── App.jsx                     # Main application
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Key Technologies

- **React 18.3** - UI framework
- **Vite 6.0** - Build tool and dev server
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Wavesurfer.js 7.8** - Audio waveform visualization
- **React Dropzone 14.3** - File upload interface
- **Lucide React** - Icon library

## API Client Features

The API client (`src/services/api.js`) includes:

- **Automatic Retries**: Retries failed requests up to 3 times
- **Error Handling**: Custom `APIError` class with detailed error info
- **Network Detection**: Detects and handles network errors
- **Exponential Backoff**: Increasing delay between retries

## State Management

The application uses React hooks for state management:

- **App-level state**: File uploads, configuration, job tracking
- **useJobManager hook**: Job polling, progress updates, cancellation
- **useAudioUpload hook**: Upload progress and status

## Error Handling

Errors are displayed via toast notifications in the top-right corner. The error system includes:

- API errors with status codes
- Network errors with retry logic
- User-friendly error messages
- Dismissible notifications

## Styling

The application uses Tailwind CSS with a custom dark theme:

- **Primary color**: Sky blue (`#0ea5e9`)
- **Accent color**: Purple (`#a855f7`)
- **Background**: Dark gray (`#111827`)
- **Cards**: Lighter gray (`#1f2937`)

## Troubleshooting

### Backend Connection Issues

If you see "Backend Offline" errors:

1. Ensure the backend is running: `python audio_backend/main.py`
2. Check that the backend is on port 8000
3. Verify CORS is enabled in the backend
4. Check browser console for network errors

### Waveform Not Loading

If waveforms don't display:

1. Ensure audio files are accessible via the API
2. Check browser console for CORS errors
3. Verify the preview/download URLs are correct

### Build Errors

If you encounter build errors:

1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Clear Vite cache: `rm -rf node_modules/.vite`

## Development Tips

- Use React DevTools for debugging component state
- Check the Network tab for API call details
- Use `console.log` in hooks to trace state changes
- Enable source maps for better debugging

## Performance Optimization

The application is optimized for RTX 3070 with 8GB VRAM:

- Segment-based processing (default 30s segments)
- Max 2 concurrent segments
- Automatic GPU cache clearing
- Progressive waveform rendering

## License

Part of the Wan2GP project. See main LICENSE.txt for details.
