import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';

const useWavesurfer = (containerRef, options = {}) => {
  const wavesurferRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;

    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#4f46e5',
      progressColor: '#818cf8',
      cursorColor: '#c7d2fe',
      barWidth: 2,
      barRadius: 3,
      cursorWidth: 1,
      height: 128,
      barGap: 1,
      ...options,
    });

    wavesurfer.on('ready', () => {
      setIsReady(true);
      setDuration(wavesurfer.getDuration());
    });

    wavesurfer.on('play', () => setIsPlaying(true));
    wavesurfer.on('pause', () => setIsPlaying(false));
    
    wavesurfer.on('audioprocess', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurfer.on('seek', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurferRef.current = wavesurfer;

    return () => {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy();
      }
    };
  }, [containerRef]);

  const play = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.play();
    }
  };

  const pause = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.pause();
    }
  };

  const stop = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.stop();
    }
  };

  const seek = (time) => {
    if (wavesurferRef.current) {
      wavesurferRef.current.seekTo(time / duration);
    }
  };

  const loadAudio = (url) => {
    if (wavesurferRef.current) {
      wavesurferRef.current.load(url);
    }
  };

  const loadPeaks = (peaks, duration) => {
    if (wavesurferRef.current && peaks) {
      wavesurferRef.current.load('', peaks, duration);
    }
  };

  return {
    wavesurfer: wavesurferRef.current,
    isReady,
    isPlaying,
    currentTime,
    duration,
    play,
    pause,
    stop,
    seek,
    loadAudio,
    loadPeaks,
  };
};

export default useWavesurfer;
