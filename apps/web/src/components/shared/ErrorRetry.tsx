import React from 'react';
import { RefreshCcw, AlertTriangle } from 'lucide-react';

interface ErrorRetryProps {
  message?: string;
  onRetry: () => void;
}

export const ErrorRetry: React.FC<ErrorRetryProps> = ({ 
  message = "Failed to load data", 
  onRetry 
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 rounded-2xl bg-red-500/5 border border-red-500/10">
      <AlertTriangle className="w-12 h-12 text-red-400 mb-4 opacity-50" />
      <p className="text-white/70 mb-6 font-medium">{message}</p>
      <button
        onClick={onRetry}
        className="flex items-center space-x-2 px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-full transition-all active:scale-95"
      >
        <RefreshCcw className="w-4 h-4" />
        <span>Retry Now</span>
      </button>
    </div>
  );
};
