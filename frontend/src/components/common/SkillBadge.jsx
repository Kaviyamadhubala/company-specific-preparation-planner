import React from 'react';

export const SkillBadge = ({ status, text }) => {
  const getColors = () => {
    switch (status) {
      case 'ready':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'needs_improvement':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'major_gap':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'not_started':
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getLabel = () => {
    if (text) return text;
    switch (status) {
      case 'ready':
        return 'Ready';
      case 'needs_improvement':
        return 'Needs Improvement';
      case 'major_gap':
        return 'Major Gap';
      case 'not_started':
      default:
        return 'Not Started';
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getColors()}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === 'ready'
            ? 'bg-emerald-500'
            : status === 'needs_improvement'
            ? 'bg-amber-500'
            : status === 'major_gap'
            ? 'bg-rose-500'
            : 'bg-slate-400'
        }`}
      />
      {getLabel()}
    </span>
  );
};

export default SkillBadge;
