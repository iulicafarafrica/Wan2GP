import React from 'react';
import { downloadResult } from '../services/api';

const ProcessingStatus = ({ jobId, status, progress, message, onDownload, onClear }) => {
  if (!jobId) return null;

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 border-green-500 text-green-800';
      case 'failed':
        return 'bg-red-100 border-red-500 text-red-800';
      case 'processing':
        return 'bg-blue-100 border-blue-500 text-blue-800';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-800';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      case 'processing':
        return (
          <svg className="w-6 h-6 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`border-2 rounded-lg p-6 ${getStatusColor()}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <div className="flex-shrink-0">
            {getStatusIcon()}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-2">
              {status === 'completed' && 'Processing Complete!'}
              {status === 'failed' && 'Processing Failed'}
              {status === 'processing' && 'Processing...'}
              {status === 'queued' && 'Queued'}
            </h3>
            <p className="text-sm mb-3">{message}</p>
            
            {status === 'processing' && (
              <div className="w-full bg-white bg-opacity-50 rounded-full h-3 mb-2">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${progress * 100}%` }}
                ></div>
              </div>
            )}
            
            {status === 'processing' && (
              <p className="text-xs">{Math.round(progress * 100)}% complete</p>
            )}
          </div>
        </div>

        <div className="flex space-x-2 ml-4">
          {status === 'completed' && (
            <a
              href={downloadResult(jobId)}
              download
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Download
            </a>
          )}
          
          <button
            onClick={onClear}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProcessingStatus;
