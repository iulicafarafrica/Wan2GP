/**
 * API Service for Wan2GP Audio Studio Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

class AudioAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const config = { ...defaultOptions, ...options };

    // Handle file uploads separately
    if (config.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Health check
  async getHealth() {
    return this.request('/health');
  }

  // Upload audio
  async uploadAudio(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('/upload', {
      method: 'POST',
      body: formData,
    });
  }

  // Start job
  async startJob(config, segments) {
    return this.request('/jobs/start', {
      method: 'POST',
      body: JSON.stringify({ config, segments }),
    });
  }

  // Get job progress
  async getJobProgress(jobId) {
    return this.request(`/jobs/${jobId}/progress`);
  }

  // Get job details
  async getJob(jobId) {
    return this.request(`/jobs/${jobId}`);
  }

  // List jobs
  async listJobs(limit = 50, statusFilter = null) {
    let endpoint = `/jobs?limit=${limit}`;
    if (statusFilter) {
      endpoint += `&status_filter=${statusFilter}`;
    }
    return this.request(endpoint);
  }

  // Cancel job
  async cancelJob(jobId) {
    return this.request(`/jobs/${jobId}`, {
      method: 'DELETE',
    });
  }

  // Get preview
  async getPreviewUrl(jobId, segmentIndex = null) {
    let endpoint = `/jobs/${jobId}/preview`;
    if (segmentIndex !== null) {
      endpoint += `?segment_index=${segmentIndex}`;
    }
    return `${this.baseUrl}${endpoint}`;
  }

  // Download result
  async getDownloadUrl(jobId) {
    return `${this.baseUrl}/jobs/${jobId}/download`;
  }

  // Get job segments
  async getJobSegments(jobId) {
    return this.request(`/jobs/${jobId}/segments`);
  }

  // Get model status
  async getModelStatus() {
    return this.request('/models/status');
  }

  // Load model
  async loadModel(modelType, modelPath = null) {
    let endpoint = `/models/load/${modelType}`;
    if (modelPath) {
      endpoint += `?model_path=${encodeURIComponent(modelPath)}`;
    }
    return this.request(endpoint, {
      method: 'POST',
    });
  }

  // Get RTX 3070 profile
  async getRTX3070Profile() {
    return this.request('/optimization/rtx3070');
  }
}

// Create and export singleton instance
export const audioAPI = new AudioAPI(API_BASE_URL);

export default audioAPI;
