import { XCircle, X } from 'lucide-react';
import { cn } from '../utils/cn';

export function ErrorNotification({ error, onClose, className }) {
  if (!error) return null;

  return (
    <div className={cn(
      'fixed top-4 right-4 max-w-md bg-red-600/90 backdrop-blur-sm text-white rounded-lg shadow-xl p-4 z-50 animate-slide-in',
      className
    )}>
      <div className="flex items-start gap-3">
        <XCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold mb-1">Error</h4>
          <p className="text-sm text-red-100">{error}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 p-1 hover:bg-red-700 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
