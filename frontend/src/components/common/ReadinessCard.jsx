import React from 'react';
import { Award, AlertCircle, CheckCircle2 } from 'lucide-react';

const ReadinessCard = ({ score = 0, companyName, roleName, isEligible = true, eligibilityNote }) => {
  const getScoreColor = (val) => {
    if (val >= 80) return 'text-emerald-600 stroke-emerald-500';
    if (val >= 60) return 'text-amber-600 stroke-amber-500';
    return 'text-rose-600 stroke-rose-500';
  };

  const getBadgeClass = (val) => {
    if (val >= 80) return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    if (val >= 60) return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-rose-50 text-rose-700 border-rose-200';
  };

  const getStatusText = (val) => {
    if (val >= 85) return 'Highly Prepared';
    if (val >= 70) return 'Competitive';
    if (val >= 50) return 'Needs Targeted Prep';
    return 'Early Preparation';
  };

  const circumference = 2 * Math.PI * 42; // r=42
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="relative overflow-hidden rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-2 text-center sm:text-left">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${getBadgeClass(score)}`}>
              <Award className="h-3.5 w-3.5" />
              {getStatusText(score)}
            </span>
            <span className="text-xs text-slate-400 font-medium">Weighted Readiness Engine</span>
          </div>

          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            {companyName ? `${companyName} Readiness Score` : 'Company Readiness Score'}
          </h3>
          {roleName && (
            <p className="text-sm font-medium text-slate-500">
              Role: <span className="font-semibold text-slate-700">{roleName}</span>
            </p>
          )}

          <div className="flex items-center gap-2 pt-1 text-xs">
            {isEligible ? (
              <span className="inline-flex items-center gap-1 text-emerald-600 font-medium">
                <CheckCircle2 className="h-4 w-4" /> Meets eligibility criteria
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-amber-600 font-medium">
                <AlertCircle className="h-4 w-4" /> {eligibilityNote || "Criteria criteria warning"}
              </span>
            )}
          </div>
        </div>

        {/* Circular Progress Meter */}
        <div className="relative flex h-32 w-32 shrink-0 items-center justify-center">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
            <circle
              className="text-slate-100"
              strokeWidth="8"
              stroke="currentColor"
              fill="transparent"
              r="42"
              cx="50"
              cy="50"
            />
            <circle
              className={`transition-all duration-1000 ease-out ${getScoreColor(score)}`}
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
              r="42"
              cx="50"
              cy="50"
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center">
            <span className="text-3xl font-black tracking-tight text-slate-900">{score}%</span>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Match</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReadinessCard;
