import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import WaveformPlayer from './components/WaveformPlayer';
import ProcessingControls from './components/ProcessingControls';
import ProcessingStatus from './components/ProcessingStatus';
import { uploadAudio, processAudio, getJobStatus, getWaveformData, checkHealth } from './services/api';

function App() {
  const [audioId, setAudioId] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [waveformData, setWaveformData] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [serverHealth, setServerHealth] = useState(null);

  useEffect(() => {
    checkServerHealth();
  }, []);

  useEffect(() => {
    let interval;
    if (jobId && processing) {
      interval = setInterval(async () => {
        try {
          const status = await getJobStatus(jobId);
          setJobStatus(status);
          
          if (status.status === 'completed' || status.status === 'failed') {
            setProcessing(false);
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error fetching job status:', error);
        }
      }, 2000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [jobId, processing]);

  const checkServerHealth = async () => {
    try {
      const health = await checkHealth();
      setServerHealth(health);
    } catch (error) {
      console.error('Error checking server health:', error);
      setServerHealth({ status: 'unhealthy', error: error.message });
    }
  };

  const handleUpload = async (file, setProgress) => {
    setUploading(true);
    try {
      const result = await uploadAudio(file, setProgress);
      setAudioId(result.audio_id);
      setAudioFile(file);
      
      const waveform = await getWaveformData(result.audio_id);
      setWaveformData(waveform);
      
      setProgress(0);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload audio: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleProcess = async (settings) => {
    if (!audioId) {
      alert('Please upload an audio file first');
      return;
    }

    setProcessing(true);
    try {
      const result = await processAudio({
        audio_id: audioId,
        ...settings
      });
      
      setJobId(result.job_id);
      setJobStatus({
        status: result.status,
        progress: 0,
        message: result.message
      });
    } catch (error) {
      console.error('Processing error:', error);
      alert('Failed to start processing: ' + error.message);
      setProcessing(false);
    }
  };

  const handleClearJob = () => {
    setJobId(null);
    setJobStatus(null);
    setProcessing(false);
  };

  const handleNewUpload = () => {
    setAudioId(null);
    setAudioFile(null);
    setWaveformData(null);
    setJobId(null);
    setJobStatus(null);
    setProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                🎤 Cover Studio
              </h1>
              <p className="text-gray-600">
                AI-powered full-length cover generation with voice conversion
              </p>
            </div>
            
            {serverHealth && (
              <div className={`px-4 py-2 rounded-lg ${
                serverHealth.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                <span className="font-semibold">Server: </span>
                {serverHealth.status === 'healthy' ? '🟢 Online' : '🔴 Offline'}
              </div>
            )}
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-semibold">Audio Input</h2>
                {audioFile && (
                  <button
                    onClick={handleNewUpload}
                    className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Upload New File
                  </button>
                )}
              </div>
              
              {!audioFile ? (
                <FileUpload onUpload={handleUpload} loading={uploading} />
              ) : (
                <div>
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">File:</span> {audioFile.name}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">Size:</span> {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  
                  {waveformData && (
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Waveform Preview</h3>
                      <WaveformPlayer waveformData={waveformData} />
                    </div>
                  )}
                </div>
              )}
            </div>

            {jobStatus && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-4">Processing Status</h2>
                <ProcessingStatus
                  jobId={jobId}
                  status={jobStatus.status}
                  progress={jobStatus.progress || 0}
                  message={jobStatus.message}
                  onClear={handleClearJob}
                />
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-8">
              <h2 className="text-2xl font-semibold mb-6">Processing Settings</h2>
              <ProcessingControls
                onProcess={handleProcess}
                disabled={!audioId || processing}
              />
            </div>
          </div>
        </div>

        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Powered by SwiftF0, SVC, and HeartMuLa/ACE-Step</p>
          <p className="mt-2">
            <a href="/docs" className="text-primary-600 hover:text-primary-700">API Documentation</a>
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
