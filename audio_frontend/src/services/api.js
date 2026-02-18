/**
 * API Service for Wan2GP Audio Studio Backend
 */

// In development, use empty string to leverage Vite proxy
// In production, use the full API URL from environment variable
const API_BASE_URL = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000');

/**
 * Custom error class for API errors
 */
class APIError extends Error {
  constructor(message, status, endpoint, originalError) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.endpoint = endpoint;
    this.originalError = originalError;
  }
}

class AudioAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.requestQueue = [];
    this.maxRetries = 3;
    this.retryDelay = 1000;
  }

  /**
   * Make an API request with error handling and retries
   */
  async request(endpoint, options = {}, retryCount = 0) {
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
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}`;
        
        // Retry on server errors (5xx) or network issues
        if (response.status >= 500 && retryCount < this.maxRetries) {
          console.warn(`Request failed with ${response.status}, retrying... (${retryCount + 1}/${this.maxRetries})`);
          await this.sleep(this.retryDelay * (retryCount + 1));
          return this.request(endpoint, options, retryCount + 1);
        }
        
        throw new APIError(errorMessage, response.status, endpoint);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return response;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Network error or timeout - retry if not exceeded max retries
      if (retryCount < this.maxRetries && this.isNetworkError(error)) {
        console.warn(`Network error, retrying... (${retryCount + 1}/${this.maxRetries})`, error.message);
        await this.sleep(this.retryDelay * (retryCount + 1));
        return this.request(endpoint, options, retryCount + 1);
      }
      
      console.error(`API Error (${endpoint}):`, error);
      throw new APIError(
        error.message || 'Network request failed',
        0,
        endpoint,
        error
      );
    }
  }

  /**
   * Check if error is a network error
   */
  isNetworkError(error) {
    return error instanceof TypeError || 
           error.message.includes('fetch') || 
           error.message.includes('network');
  }

  /**
   * Sleep utility for retries
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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

// Export error class for use in error handling
export { APIError };

export default audioAPI;
