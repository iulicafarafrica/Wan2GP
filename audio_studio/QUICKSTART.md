# Quick Start Guide

## 1. Installation (One-time)

```bash
# Install backend dependencies
pip install -r audio_backend/requirements.txt

# Install frontend dependencies
cd audio_frontend
npm install
cd ..
```

## 2. Start Application

### Option A: Use Quick Start Script (Recommended)

**Linux/Mac:**
```bash
./audio_studio/start_audio_studio.sh
```

**Windows:**
```cmd
audio_studio\start_audio_studio.bat
```

### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
python audio_backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd audio_frontend
npm run dev
```

## 3. Open Browser

Navigate to: **http://localhost:3000**

## 4. Process Audio

1. **Upload**: Drag and drop an audio file
2. **Configure**: Select profile (Fast/Balanced/Quality) or customize settings
3. **Process**: Click "Start Processing"
4. **Preview**: View segments and combined result
5. **Download**: Download final processed audio

## RTX 3070 Settings

The application is pre-configured for RTX 3070 (8GB VRAM):

- **Segment Length**: 30 seconds
- **Max Concurrent Segments**: 2
- **Sample Rate**: 48kHz
- **Bit Depth**: 16-bit

## Common Tasks

### Process with Pitch Shift
1. Upload audio
2. In Configuration → SwiftF0, set "Pitch Shift" (e.g., +2 for higher)
3. Start processing

### Voice Conversion
1. Upload source audio
2. In Configuration → SVC:
   - Select variant (so-vits-svc/hq-svc/echo)
   - Set speaker ID
3. Start processing

### Instrumental Generation
1. Upload audio with vocals
2. In Configuration → Instrumental:
   - Enable "Split Vocals"
   - Select model (ace-step recommended)
3. Start processing

### Download Only Instrumental
1. Upload audio
2. Enable Instrumental → Split Vocals
3. Disable other stages if desired
4. Start processing

## Troubleshooting

**Backend won't start?**
```bash
# Check if port 8001 is in use
lsof -i :8001
```

**Frontend won't connect?**
- Verify backend is running on http://127.0.0.1:8001
- Check browser console for errors

**Out of memory?**
- Reduce segment length to 20s
- Reduce max concurrent segments to 1

## Next Steps

- Read full documentation: `audio_studio/README.md`
- Setup guide: `audio_studio/SETUP.md`
- API documentation: http://127.0.0.1:8001/docs (when backend is running)
