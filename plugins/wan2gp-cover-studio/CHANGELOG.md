# Changelog

All notable changes to the Cover Studio plugin will be documented in this file.

## [1.0.0] - 2026-02-17

### Added
- Initial release of Cover Studio plugin for Wan2GP
- FastAPI backend server with REST API
- React frontend with Tailwind CSS styling
- Wavesurfer.js integration for audio visualization
- Placeholder model implementations:
  - SwiftF0 pitch extraction
  - SVC voice conversion (so-vits-svc/HQ-SVC/Echo)
  - Instrumental generation (HeartMuLa/ACE-Step)
- Segment-by-segment audio processing pipeline
- File upload with drag-and-drop support
- Real-time processing status and progress tracking
- Model selection interface (voice and instrumental)
- Pitch shift control (-12 to +12 semitones)
- Configurable segment processing
- Audio separation (vocals/instrumental)
- Audio mixing and post-processing utilities
- Job queue and status tracking system
- Download functionality for processed covers
- Gradio plugin integration
- Server start/stop controls in Gradio interface
- Health check endpoint
- Waveform data generation
- Comprehensive documentation:
  - README.md with full feature overview
  - QUICKSTART.md for easy onboarding
  - INTEGRATION_GUIDE.md for model integration
  - SUMMARY.md with implementation details
- Build script for frontend
- .gitignore for proper version control
- requirements.txt for dependency management
- Placeholder HTML for non-built frontend

### API Endpoints
- `POST /api/upload` - Upload audio files
- `GET /api/models/voice` - List available voice models
- `GET /api/models/instrumental` - List available instrumental models
- `POST /api/process` - Start cover processing job
- `GET /api/status/{job_id}` - Get job processing status
- `GET /api/download/{job_id}` - Download processed cover
- `DELETE /api/job/{job_id}` - Delete processing job
- `GET /api/waveform/{audio_id}` - Get waveform visualization data
- `GET /api/health` - Health check endpoint

### Frontend Components
- FileUpload - Drag-and-drop audio upload
- WaveformPlayer - Audio visualization with play/pause controls
- ProcessingControls - Model selection and settings configuration
- ProcessingStatus - Real-time job progress display
- useWavesurfer - Custom React hook for Wavesurfer.js

### Technical Details
- Python 3.10+ support
- FastAPI 0.104+ with async support
- React 18.2 with hooks
- Tailwind CSS 3.3 for styling
- Wavesurfer.js 7.7 for audio visualization
- CORS middleware for cross-origin requests
- Background task processing
- GPU memory management
- Error handling and logging
- File size validation (100MB limit)
- Multiple audio format support (MP3, WAV, FLAC, OGG, M4A)

### Documentation
- Installation instructions
- Usage guides
- API documentation
- Model integration guides
- Troubleshooting tips
- Performance optimization tips
- Example code snippets
- Architecture diagrams

## [Unreleased]

### Planned Features
- WebSocket support for real-time progress streaming
- User authentication and authorization
- Cloud storage integration (S3, Azure, GCS)
- Batch processing UI
- Multiple voice model chaining
- Advanced audio effects (reverb, EQ, compression)
- Preset management
- Export in multiple formats
- Mobile responsive improvements
- Docker containerization
- Model marketplace integration
- Plugin analytics and monitoring
- Rate limiting and quotas
- Database integration for job history
- Email notifications for completed jobs
- Social sharing features
- A/B testing for model comparison

### Known Issues
- Frontend requires Node.js build step
- No authentication/authorization yet
- Local file storage only
- No job persistence across server restarts
- Limited error recovery mechanisms

### Future Enhancements
- Support for more SVC model types
- Integration with additional pitch extraction methods
- Advanced segmentation algorithms
- Real-time preview during processing
- Model fine-tuning interface
- Custom plugin extension system
- API rate limiting
- Job prioritization
- Multi-language support
- Accessibility improvements

---

## Version History

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality additions
- PATCH version for backwards-compatible bug fixes

### Release Notes Format
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for bug fixes
- **Security** for vulnerability fixes

---

For more information, see:
- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Model integration
- [SUMMARY.md](SUMMARY.md) - Implementation details
