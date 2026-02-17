import { useRef, useEffect, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';
import { cn } from '../utils/cn';

export function WaveSurferPlayer({ 
  audioUrl, 
  className,
  height = 128,
  color = '#0ea5e9',
  progressColor = '#a855f7',
  onPlay,
  onPause,
  onReady 
}) {
  const containerRef = useRef(null);
  const wavesurferRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1.0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    if (!containerRef.current || !audioUrl) return;

    // Initialize WaveSurfer
    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#475569',
      progressColor: progressColor,
      cursorColor: color,
      barWidth: 2,
      barGap: 3,
      barRadius: 3,
      height,
      normalize: true,
      backend: 'WebAudio',
      mediaControls: false,
    });

    wavesurferRef.current = wavesurfer;

    // Load audio
    wavesurfer.load(audioUrl);

    // Event listeners
    wavesurfer.on('ready', () => {
      setDuration(wavesurfer.getDuration());
      onReady?.();
    });

    wavesurfer.on('play', () => {
      setIsPlaying(true);
      onPlay?.();
    });

    wavesurfer.on('pause', () => {
      setIsPlaying(false);
      onPause?.();
    });

    wavesurfer.on('audioprocess', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurfer.on('finish', () => {
      setIsPlaying(false);
      setCurrentTime(0);
    });

    // Cleanup
    return () => {
      wavesurfer.destroy();
    };
  }, [audioUrl, color, progressColor, height, onPlay, onPause, onReady]);

  const togglePlayPause = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
    }
  };

  const toggleMute = () => {
    if (wavesurferRef.current) {
      if (isMuted) {
        wavesurferRef.current.setVolume(volume);
      } else {
        wavesurferRef.current.setVolume(0);
      }
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (wavesurferRef.current) {
      wavesurferRef.current.setVolume(newVolume);
      setIsMuted(newVolume === 0);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn('bg-gray-800 rounded-lg p-4', className)}>
      <div ref={containerRef} className="mb-4" />
      
      <div className="flex items-center gap-4">
        {/* Play/Pause button */}
        <button
          onClick={togglePlayPause}
          className="p-2 bg-primary-600 hover:bg-primary-700 rounded-full transition-colors"
          disabled={!audioUrl}
        >
          {isPlaying ? (
            <Pause className="w-5 h-5" />
          ) : (
            <Play className="w-5 h-5 ml-0.5" />
          )}
        </button>

        {/* Time display */}
        <div className="text-sm text-gray-400 min-w-[100px]">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>

        {/* Volume control */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleMute}
            className="text-gray-400 hover:text-white transition-colors"
            disabled={!audioUrl}
          >
            {isMuted ? (
              <VolumeX className="w-4 h-4" />
            ) : (
              <Volume2 className="w-4 h-4" />
            )}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
            className="w-20 accent-primary-600"
            disabled={!audioUrl}
          />
        </div>

        {/* Progress bar (custom) */}
        <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden cursor-pointer"
             onClick={(e) => {
               const rect = e.currentTarget.getBoundingClientRect();
               const percent = (e.clientX - rect.left) / rect.width;
               if (wavesurferRef.current && duration > 0) {
                 wavesurferRef.current.seekTo(percent);
               }
             }}>
          <div 
            className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all"
            style={{ width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%' }}
          />
        </div>
      </div>
    </div>
  );
}
