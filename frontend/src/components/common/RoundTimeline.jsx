import React from 'react';
import { CheckCircle2, Clock, Zap, Award } from 'lucide-react';

const RoundTimeline = ({ rounds = [] }) => {
  if (!rounds || rounds.length === 0) {
    return <p className="text-sm text-slate-500">No recruitment rounds specified.</p>;
  }

  const sortedRounds = [...rounds].sort((a, b) => a.round_number - b.round_number);

  return (
    <div className="space-y-6">
      {/* Visual step chain on top */}
      <div className="hidden md:flex items-center justify-between overflow-x-auto pb-4 pt-2">
        {sortedRounds.map((r, idx) => (
          <React.Fragment key={r.id}>
            <div className="flex flex-col items-center min-w-[120px]">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 font-bold border-2 border-brand-500 shadow-sm shadow-brand-500/10 text-sm">
                R{r.round_number}
              </div>
              <span className="mt-2 text-xs font-semibold text-slate-800 text-center line-clamp-1 max-w-[110px]">
                {r.name}
              </span>
              <span className="text-[10px] text-slate-400 capitalize">{r.difficulty} diff</span>
            </div>
            {idx < sortedRounds.length - 1 && (
              <div className="h-0.5 flex-1 bg-gradient-to-r from-brand-300 to-indigo-200 mx-2 -mt-7" />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Detailed round cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sortedRounds.map((r) => (
          <div
            key={r.id}
            className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs transition hover:shadow-md flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="inline-flex items-center gap-1 rounded-md bg-brand-50 px-2 py-0.5 text-xs font-bold text-brand-700">
                  Round {r.round_number}
                </span>
                <span
                  className={`text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                    r.difficulty === 'hard'
                      ? 'bg-rose-50 text-rose-600 border border-rose-100'
                      : r.difficulty === 'medium'
                      ? 'bg-amber-50 text-amber-600 border border-amber-100'
                      : 'bg-emerald-50 text-emerald-600 border border-emerald-100'
                  }`}
                >
                  {r.difficulty}
                </span>
              </div>

              <h4 className="font-bold text-slate-900 text-base">{r.name}</h4>
              <p className="mt-1 text-xs text-slate-600 leading-relaxed">{r.description}</p>

              {r.tips && (
                <div className="mt-3 rounded-xl bg-slate-50 p-2.5 text-[11px] text-slate-600 border border-slate-100">
                  <span className="font-semibold text-slate-800">Preparation Tip: </span>
                  {r.tips}
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" /> ~{r.estimated_days || 3} days prep
              </span>
              <span className="text-[11px] font-medium text-brand-600">Round {r.round_number} of {sortedRounds.length}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RoundTimeline;
