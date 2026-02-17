import React, { useState, useEffect } from 'react';
import { getVoiceModels, getInstrumentalModels } from '../services/api';

const ProcessingControls = ({ onProcess, disabled }) => {
  const [voiceModels, setVoiceModels] = useState([]);
  const [instrumentalModels, setInstrumentalModels] = useState([]);
  const [selectedVoiceModel, setSelectedVoiceModel] = useState('');
  const [selectedInstrumentalModel, setSelectedInstrumentalModel] = useState('none');
  const [pitchShift, setPitchShift] = useState(0);
  const [useSegments, setUseSegments] = useState(true);
  const [segmentLength, setSegmentLength] = useState(30);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const [voiceData, instrumentalData] = await Promise.all([
        getVoiceModels(),
        getInstrumentalModels()
      ]);
      
      setVoiceModels(voiceData);
      setInstrumentalModels(instrumentalData);
      
      if (voiceData.length > 0) {
        setSelectedVoiceModel(voiceData[0].id);
      }
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const handleProcess = () => {
    if (!selectedVoiceModel) {
      alert('Please select a voice model');
      return;
    }

    onProcess({
      voice_model: selectedVoiceModel,
      instrumental_model: selectedInstrumentalModel,
      pitch_shift: pitchShift,
      use_segments: useSegments,
      segment_length: segmentLength
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Voice Model</h3>
        <select
          value={selectedVoiceModel}
          onChange={(e) => setSelectedVoiceModel(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          disabled={disabled}
        >
          {voiceModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name} ({model.type})
            </option>
          ))}
        </select>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Instrumental Model (Optional)</h3>
        <select
          value={selectedInstrumentalModel}
          onChange={(e) => setSelectedInstrumentalModel(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          disabled={disabled}
        >
          {instrumentalModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
        </select>
        <p className="mt-2 text-sm text-gray-500">
          Select 'None' to use the original instrumental from the audio file
        </p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Processing Options</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pitch Shift (semitones): {pitchShift}
            </label>
            <input
              type="range"
              min="-12"
              max="12"
              value={pitchShift}
              onChange={(e) => setPitchShift(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              disabled={disabled}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>-12</span>
              <span>0</span>
              <span>+12</span>
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="useSegments"
              checked={useSegments}
              onChange={(e) => setUseSegments(e.target.checked)}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              disabled={disabled}
            />
            <label htmlFor="useSegments" className="ml-2 text-sm text-gray-700">
              Process in segments (recommended for long audio)
            </label>
          </div>

          {useSegments && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Segment Length: {segmentLength} seconds
              </label>
              <input
                type="range"
                min="10"
                max="60"
                step="5"
                value={segmentLength}
                onChange={(e) => setSegmentLength(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                disabled={disabled}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>10s</span>
                <span>35s</span>
                <span>60s</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <button
        onClick={handleProcess}
        disabled={disabled || !selectedVoiceModel}
        className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
      >
        {disabled ? 'Processing...' : 'Start Processing'}
      </button>
    </div>
  );
};

export default ProcessingControls;
