import { Clock, CheckCircle2, XCircle, Loader2, Layers } from 'lucide-react';
import { cn } from '../utils/cn';

export function JobProgress({ 
  progress, 
  status, 
  currentStage, 
  message,
  segmentsCompleted,
  segmentsTotal,
  segments = [],
  className 
}) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'failed':
      case 'cancelled':
        return 'text-red-400';
      case 'running':
        return 'text-primary-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getSegmentStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'running':
        return 'bg-primary-500';
      default:
        return 'bg-gray-600';
    }
  };

  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Processing Progress</h3>
        {getStatusIcon(status)}
      </div>

      {/* Overall progress */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span className={getStatusColor(status)}>{status}</span>
          <span>{progress.toFixed(1)}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Current stage */}
      {currentStage && (
        <div className="mb-4 p-3 bg-gray-700/50 rounded-lg">
          <p className="text-sm text-gray-400 mb-1">Current Stage</p>
          <p className="font-medium">{currentStage}</p>
        </div>
      )}

      {/* Message */}
      {message && (
        <p className="text-sm text-gray-400 mb-4">{message}</p>
      )}

      {/* Segment progress */}
      {segmentsTotal > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Layers className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400">
              Segments: {segmentsCompleted} / {segmentsTotal}
            </span>
          </div>
          
          {/* Visual segment indicator */}
          <div className="flex gap-1 flex-wrap">
            {segments.map((segment, idx) => (
              <div
                key={idx}
                className={cn(
                  'h-2 rounded-full transition-all',
                  getSegmentStatusColor(segment.status)
                )}
                style={{ 
                  width: `${100 / Math.max(segments.length, 1)}%`,
                  minWidth: '4px'
                }}
                title={`Segment ${idx + 1}: ${segment.status}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Segment list */}
      {segments.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <h4 className="text-sm font-medium mb-2">Segment Details</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {segments.map((segment, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-sm p-2 bg-gray-700/30 rounded"
              >
                <div className="flex items-center gap-2">
                  {getStatusIcon(segment.status)}
                  <span>Segment {idx + 1}</span>
                </div>
                <div className="text-gray-400">
                  {segment.start_time.toFixed(1)}s - {segment.end_time.toFixed(1)}s
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
