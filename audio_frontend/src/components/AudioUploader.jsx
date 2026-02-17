import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, Music, X } from 'lucide-react';
import { cn } from '../utils/cn';
import { useAudioUpload } from '../hooks/useAudioUpload';

export function AudioUploader({ onFileUploaded, className }) {
  const { uploading, uploadProgress, uploadedFile, error, uploadAudio, reset } = useAudioUpload();

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      try {
        const result = await uploadAudio(file);
        onFileUploaded?.(result);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    }
  }, [uploadAudio, onFileUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
    },
    multiple: false,
    disabled: uploading
  });

  const handleReset = () => {
    reset();
    onFileUploaded?.(null);
  };

  if (uploadedFile) {
    return (
      <div className={cn('card', className)}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Uploaded Audio</h3>
          <button
            onClick={handleReset}
            className="p-1 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex items-center gap-3 mb-3">
          <div className="p-3 bg-accent-600/20 rounded-lg">
            <Music className="w-6 h-6 text-accent-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{uploadedFile.filename}</p>
            <p className="text-sm text-gray-400">
              {(uploadedFile.file_size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        </div>

        <div className="text-sm text-gray-400">
          <p><strong>File ID:</strong> {uploadedFile.file_id}</p>
          <p><strong>Status:</strong> Ready to process</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('card', className)}>
      <h3 className="text-lg font-semibold mb-4">Upload Audio</h3>
      
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all',
          'hover:border-primary-500 hover:bg-gray-700/50',
          isDragActive && 'border-primary-500 bg-gray-700/50',
          uploading && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-4">
          <div className={cn(
            'p-4 rounded-full',
            isDragActive ? 'bg-primary-600' : 'bg-gray-700'
          )}>
            <UploadCloud className={cn('w-8 h-8', isDragActive ? 'text-white' : 'text-gray-400')} />
          </div>
          
          <div>
            <p className="text-lg font-medium mb-1">
              {isDragActive ? 'Drop audio file here' : 'Drag & drop audio file'}
            </p>
            <p className="text-sm text-gray-400">
              or click to browse (WAV, MP3, FLAC, OGG)
            </p>
          </div>
        </div>
      </div>

      {uploading && (
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-2">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-600/20 border border-red-600/50 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}
    </div>
  );
}
