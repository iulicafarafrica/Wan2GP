import { useState, useEffect, useCallback, useRef } from 'react';
import { audioAPI } from '../services/api';

export function useJobManager(jobId = null) {
  const [job, setJob] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const pollingIntervalRef = useRef(null);
  const [segments, setSegments] = useState([]);

  // Start a new job
  const startJob = useCallback(async (config, segmentsData) => {
    try {
      setLoading(true);
      setError(null);

      const result = await audioAPI.startJob(config, segmentsData);
      
      return result.job_id;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Poll for job progress
  const startPolling = useCallback((id) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    pollingIntervalRef.current = setInterval(async () => {
      try {
        const progressData = await audioAPI.getJobProgress(id);
        setJob(progressData);
        setProgress(progressData.progress);
        setStatus(progressData.status);

        // Stop polling if job is complete
        if (['completed', 'failed', 'cancelled'].includes(progressData.status)) {
          stopPolling();
          // Load full job details
          const fullJob = await audioAPI.getJob(id);
          setJob(fullJob);
          
          // Load segments
          try {
            const segmentsData = await audioAPI.getJobSegments(id);
            setSegments(segmentsData.segments);
          } catch (e) {
            console.error('Failed to load segments:', e);
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
        setError(err.message);
        // Don't stop polling on transient errors
      }
    }, 2000); // Poll every 2 seconds
  }, []);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  // Load job details
  const loadJob = useCallback(async (id) => {
    try {
      setLoading(true);
      setError(null);

      const jobData = await audioAPI.getJob(id);
      setJob(jobData);
      setStatus(jobData.status);
      setProgress(jobData.progress);

      // Load segments
      try {
        const segmentsData = await audioAPI.getJobSegments(id);
        setSegments(segmentsData.segments);
      } catch (e) {
        console.error('Failed to load segments:', e);
      }

      return jobData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Cancel job
  const cancelJob = useCallback(async (id) => {
    try {
      await audioAPI.cancelJob(id);
      setStatus('cancelled');
      stopPolling();
      
      // Reload job details
      await loadJob(id);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [loadJob, stopPolling]);

  // Start polling when jobId changes
  useEffect(() => {
    if (jobId && !['completed', 'failed', 'cancelled'].includes(status)) {
      loadJob(jobId);
      startPolling(jobId);
    }

    return () => {
      stopPolling();
    };
  }, [jobId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    job,
    progress,
    status,
    loading,
    error,
    segments,
    startJob,
    loadJob,
    cancelJob,
    startPolling,
    stopPolling,
  };
}
