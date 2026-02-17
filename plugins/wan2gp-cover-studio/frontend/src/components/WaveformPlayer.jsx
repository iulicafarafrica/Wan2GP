import React, { useRef, useEffect } from 'react';
import useWavesurfer from '../hooks/useWavesurfer';

const WaveformPlayer = ({ audioUrl, waveformData }) => {
  const containerRef = useRef(null);
  const { isReady, isPlaying, currentTime, duration, play, pause, loadAudio, loadPeaks } = useWavesurfer(containerRef);

  useEffect(() => {
    if (audioUrl) {
      loadAudio(audioUrl);
    } else if (waveformData) {
      loadPeaks([waveformData.samples], waveformData.duration);
    }
  }, [audioUrl, waveformData]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full">
      <div ref={containerRef} className="waveform-container mb-4" />
      
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-4">
          <button
            onClick={isPlaying ? pause : play}
            disabled={!isReady}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isPlaying ? (
              <span className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Pause
              </span>
            ) : (
              <span className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                Play
              </span>
            )}
          </button>
          
          <div className="text-sm text-gray-600">
            {formatTime(currentTime)} / {formatTime(duration)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WaveformPlayer;
