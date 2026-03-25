import React from 'react';

export const LoadingSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => {
  return (
    <div className="w-full space-y-4 py-4">
      {[...Array(rows)].map((_, i) => (
        <div 
          key={i} 
          className="h-16 w-full bg-white/5 rounded-xl animate-pulse flex items-center px-6 space-x-4"
        >
          <div className="h-8 w-8 bg-white/10 rounded-full" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-1/4 bg-white/10 rounded" />
            <div className="h-2 w-1/3 bg-white/5 rounded" />
          </div>
          <div className="h-8 w-24 bg-white/10 rounded-lg" />
        </div>
      ))}
    </div>
  );
};
