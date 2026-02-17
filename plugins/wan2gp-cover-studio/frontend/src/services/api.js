import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8765/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadAudio = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    },
  });

  return response.data;
};

export const getVoiceModels = async () => {
  const response = await api.get('/models/voice');
  return response.data;
};

export const getInstrumentalModels = async () => {
  const response = await api.get('/models/instrumental');
  return response.data;
};

export const processAudio = async (processRequest) => {
  const response = await api.post('/process', processRequest);
  return response.data;
};

export const getJobStatus = async (jobId) => {
  const response = await api.get(`/status/${jobId}`);
  return response.data;
};

export const downloadResult = (jobId) => {
  return `${API_BASE_URL}/download/${jobId}`;
};

export const deleteJob = async (jobId) => {
  const response = await api.delete(`/job/${jobId}`);
  return response.data;
};

export const getWaveformData = async (audioId) => {
  const response = await api.get(`/waveform/${audioId}`);
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
