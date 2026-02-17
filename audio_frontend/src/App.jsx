import { useState, useEffect } from 'react';
import { Play, Download, RefreshCw, Server, Music, CheckCircle, AlertCircle } from 'lucide-react';
import { AudioUploader } from './components/AudioUploader';
import { WaveSurferPlayer } from './components/WaveSurferPlayer';
import { JobProgress } from './components/JobProgress';
import { ConfigForm } from './components/ConfigForm';
import { useJobManager } from './hooks/useJobManager';
import { audioAPI } from './services/api';
import { cn } from './utils/cn';

// Default configuration optimized for RTX 3070
const defaultConfig = {
  processing: {
    segment_length: 30.0,
    overlap_duration: 0.5,
    max_concurrent_segments: 2,
    use_gpu: true,
    device: 'cuda',
    clear_cache_between_segments: true
  },
  quality: {
    sample_rate: 48000,
    bit_depth: 16,
    channels: 2,
    output_format: 'wav'
  },
  swiftf0: {
    enabled: true,
    pitch_shift: 0,
    formant_shift: 1.0,
    extract_f0_only: false,
    preserve_vibrato: true
  },
  svc: {
    enabled: true,
    variant: 'so-vits-svc',
    model_path: null,
    speaker_id: null,
    f0_method: 'fcpe',
    f0_min: 50,
    f0_max: 1100,
    cluster_infer_ratio: 0.0,
    noise_scale: 0.4,
    auto_predict_f0: false
  },
  instrumental: {
    enabled: true,
    model: 'ace-step',
    model_path: null,
    split_vocals: true,
    keep_reverb: false,
    stem_separation: false,
    stems: ['vocals', 'drums', 'bass', 'other']
  },
  mixing: {
    enabled: true,
    vocal_volume: 1.0,
    instrumental_volume: 1.0,
    fade_in: 0.0,
    fade_out: 0.0,
    crossfade_segments: true,
    crossfade_duration: 0.5
  },
  pipeline_stages: ['swiftf0', 'svc', 'instrumental', 'mixing'],
  metadata: {}
};

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [config, setConfig] = useState(defaultConfig);
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [modelStatus, setModelStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');

  const { job, progress, status, segments, startJob, cancelJob } = useJobManager(job?.job_id);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  // Auto-switch to progress tab when job starts
  useEffect(() => {
    if (status && status !== 'queued' && status !== 'unknown') {
      setActiveTab('progress');
    }
  }, [status]);

  const checkBackendHealth = async () => {
    try {
      const health = await audioAPI.getHealth();
      setBackendStatus('healthy');
      
      // Also get model status
      try {
        const models = await audioAPI.getModelStatus();
        setModelStatus(models);
      } catch (e) {
        console.error('Failed to get model status:', e);
      }
    } catch (e) {
      setBackendStatus('unhealthy');
      console.error('Backend health check failed:', e);
    }
  };

  const handleFileUploaded = (fileData) => {
    setUploadedFile(fileData);
    setActiveTab('config');
  };

  const handleStartProcessing = async () => {
    if (!uploadedFile) {
      alert('Please upload an audio file first');
      return;
    }

    try {
      // Create segments (for now, just one segment covering the whole file)
      // In a real implementation, you might want to segment based on silence, etc.
      const segments = [
        {
          start_time: 0.0,
          end_time: 30.0,  // Will be updated based on actual duration
          original_path: uploadedFile.file_path
        }
      ];

      const jobId = await startJob(config, segments);
      console.log('Job started:', jobId);
    } catch (e) {
      alert(`Failed to start job: ${e.message}`);
    }
  };

  const handleDownload = () => {
    if (job?.job_id) {
      const downloadUrl = audioAPI.getDownloadUrl(job.job_id);
      window.open(downloadUrl, '_blank');
    }
  };

  const handleReset = () => {
    setUploadedFile(null);
    setConfig(defaultConfig);
    setActiveTab('upload');
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg">
              <Music className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Wan2GP Audio Studio</h1>
              <p className="text-sm text-gray-400">Segment-based Audio Processing Pipeline</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Backend Status */}
            <button
              onClick={checkBackendHealth}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors',
                backendStatus === 'healthy' ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
              )}
            >
              <Server className="w-4 h-4" />
              {backendStatus === 'healthy' ? 'Backend Online' : 'Backend Offline'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('upload')}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'upload' ? 'bg-primary-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            )}
          >
            1. Upload
          </button>
          <button
            onClick={() => setActiveTab('config')}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'config' ? 'bg-primary-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            )}
            disabled={!uploadedFile}
          >
            2. Configure
          </button>
          <button
            onClick={() => setActiveTab('progress')}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'progress' ? 'bg-primary-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            )}
            disabled={!job}
          >
            3. Progress
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'preview' ? 'bg-primary-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            )}
            disabled={status !== 'completed'}
          >
            4. Preview & Download
          </button>
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {activeTab === 'upload' && (
              <AudioUploader onFileUploaded={handleFileUploaded} />
            )}

            {activeTab === 'config' && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Processing Configuration</h3>
                
                <ConfigForm 
                  config={config}
                  onChange={setConfig}
                />

                <div className="mt-6 flex gap-3">
                  <button
                    onClick={handleStartProcessing}
                    className="btn btn-primary flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Start Processing
                  </button>
                  
                  <button
                    onClick={handleReset}
                    className="btn btn-secondary"
                  >
                    Reset
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'progress' && (
              <JobProgress
                progress={progress}
                status={status}
                currentStage={job?.current_stage}
                message={job?.message}
                segmentsCompleted={job?.segments_completed}
                segmentsTotal={job?.segments_total}
                segments={segments}
              />
            )}

            {activeTab === 'preview' && status === 'completed' && (
              <div className="space-y-6">
                {/* Preview Player */}
                {job?.preview_url && (
                  <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Preview Result</h3>
                    <WaveSurferPlayer
                      audioUrl={job.preview_url}
                      height={160}
                    />
                  </div>
                )}

                {/* Segment Previews */}
                {segments.length > 0 && (
                  <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Segment Previews</h3>
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {segments.map((segment, idx) => (
                        segment.preview_path && (
                          <div key={idx} className="p-3 bg-gray-700/30 rounded-lg">
                            <p className="text-sm font-medium mb-2">Segment {idx + 1}</p>
                            <WaveSurferPlayer
                              audioUrl={`/api${segment.preview_path}`}
                              height={80}
                            />
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                )}

                {/* Download Button */}
                <button
                  onClick={handleDownload}
                  className="btn btn-accent flex items-center gap-2 w-full justify-center"
                >
                  <Download className="w-4 h-4" />
                  Download Final Result
                </button>

                {/* Reset Button */}
                <button
                  onClick={handleReset}
                  className="btn btn-secondary flex items-center gap-2 w-full justify-center"
                >
                  <RefreshCw className="w-4 h-4" />
                  Process Another File
                </button>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Model Status */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Model Status</h3>
              
              {modelStatus ? (
                <div className="space-y-3">
                  <ModelStatusItem
                    name="SwiftF0"
                    available={modelStatus.swiftf0?.available}
                    loaded={modelStatus.swiftf0?.loaded}
                  />
                  <ModelStatusItem
                    name="SVC"
                    available={modelStatus.svc?.available}
                    loaded={modelStatus.svc?.loaded}
                  />
                  <ModelStatusItem
                    name="Instrumental"
                    available={modelStatus.instrumental?.available}
                    loaded={modelStatus.instrumental?.loaded}
                  />
                </div>
              ) : (
                <p className="text-sm text-gray-400">Loading model status...</p>
              )}
            </div>

            {/* RTX 3070 Tips */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                RTX 3070 Optimized
              </h3>
              
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-primary-400 mt-1">•</span>
                  <span>Segment-by-segment processing for 8GB VRAM</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-400 mt-1">•</span>
                  <span>Max 2 concurrent segments</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-400 mt-1">•</span>
                  <span>Automatic GPU cache clearing</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-400 mt-1">•</span>
                  <span>30-second segments recommended</span>
                </li>
              </ul>
            </div>

            {/* System Info */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">System Info</h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Backend</span>
                  <span>{backendStatus}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">API URL</span>
                  <span className="text-xs truncate max-w-32">http://127.0.0.1:8001</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function ModelStatusItem({ name, available, loaded }) {
  return (
    <div className="flex items-center justify-between p-2 bg-gray-700/30 rounded">
      <span className="font-medium">{name}</span>
      <div className="flex items-center gap-2">
        {available ? (
          <CheckCircle className="w-4 h-4 text-green-400" />
        ) : (
          <AlertCircle className="w-4 h-4 text-yellow-400" />
        )}
        {loaded && <span className="text-xs bg-primary-600 px-2 py-0.5 rounded">Loaded</span>}
      </div>
    </div>
  );
}

export default App;
