import { useState, useCallback } from 'react';
import { audioAPI } from '../services/api';

export function useAudioUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [error, setError] = useState(null);

  const uploadAudio = useCallback(async (file) => {
    try {
      setUploading(true);
      setError(null);
      setUploadProgress(0);

      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const result = await audioAPI.uploadAudio(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadedFile(result);

      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setUploading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setUploading(false);
    setUploadProgress(0);
    setUploadedFile(null);
    setError(null);
  }, []);

  return {
    uploading,
    uploadProgress,
    uploadedFile,
    error,
    uploadAudio,
    reset,
  };
}
