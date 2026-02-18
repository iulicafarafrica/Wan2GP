import { Loader2 } from 'lucide-react';
import { cn } from '../utils/cn';

export function LoadingSpinner({ size = 'md', className, text }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 className={cn('animate-spin text-primary-500', sizeClasses[size])} />
      {text && <p className="text-sm text-gray-400">{text}</p>}
    </div>
  );
}
