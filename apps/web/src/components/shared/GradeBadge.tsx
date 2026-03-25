import React from 'react';

interface GradeBadgeProps {
  grade: string;
  className?: string;
}

export const GradeBadge: React.FC<GradeBadgeProps> = ({ grade, className = '' }) => {
  const getGradeStyle = (g: string) => {
    const base = 'px-2 py-1 rounded-md text-xs font-bold uppercase tracking-tighter';
    switch (g?.toUpperCase()) {
      case 'A':
        return `${base} bg-green-500/20 text-green-400 border border-green-500/30`;
      case 'B':
        return `${base} bg-blue-500/20 text-blue-400 border border-blue-500/30`;
      case 'C':
        return `${base} bg-yellow-500/20 text-yellow-400 border border-yellow-500/30`;
      case 'F':
        return `${base} bg-red-500/20 text-red-400 border border-red-500/30`;
      default:
        return `${base} bg-white/10 text-white/50 border border-white/20`;
    }
  };

  return <span className={`${getGradeStyle(grade)} ${className}`}>{grade || 'N/A'}</span>;
};
