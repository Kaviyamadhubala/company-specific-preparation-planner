import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import {
  Scale,
  Building2,
  ArrowRight,
  Sparkles,
  Award,
  AlertCircle,
  HelpCircle,
  Info
} from 'lucide-react';

const CompanyComparison = () => {
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComparison();
  }, []);

  const fetchComparison = async () => {
    try {
      setLoading(true);
      const res = await api.get('/readiness/compare/all');
      setComparisons(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-bold text-brand-700 mb-2">
          <Sparkles className="h-3.5 w-3.5" /> Multi-Company Benchmarking
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Cross-Company Readiness Comparison
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Evaluate how your current technical profile stacks up across recruiters with varying difficulty thresholds
        </p>
      </div>

      {/* Comparison Explanatory Callout */}
      <div className="rounded-2xl border border-indigo-100 bg-indigo-50/60 p-5 text-xs text-indigo-900 flex items-start gap-3 shadow-2xs">
        <Info className="h-5 w-5 text-brand-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold">Why do readiness scores differ across companies?</p>
          <p className="text-slate-600 leading-relaxed">
            Each company configures distinct required proficiency levels and interview round standards.
            For example, <span className="font-bold text-slate-800">Zoho</span> demands Advanced DSA and
            problem-solving, lowering scores for beginner DSA students, while{' '}
            <span className="font-bold text-slate-800">TCS</span> prioritizes core OOP and general aptitude.
          </p>
        </div>
      </div>

      {/* Comparison Table / Cards */}
      <div className="space-y-3">
        {comparisons.map((c, idx) => (
          <div
            key={c.company_id}
            className="rounded-3xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition hover:shadow-md"
          >
            <div className="flex items-center gap-4">
              <div
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-white font-black text-base shadow-sm"
                style={{ backgroundColor: c.logo_color || '#4f46e5' }}
              >
                {c.logo_initials || c.company_name.slice(0, 3).toUpperCase()}
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-slate-900 text-base">{c.company_name}</h3>
                  <span className="capitalize text-[10px] font-bold bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                    {c.difficulty}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Target Profile: <span className="font-semibold text-slate-700">{c.target_role}</span>
                </p>
                {c.weak_areas?.length > 0 && (
                  <p className="text-[11px] text-rose-600 mt-1 font-medium">
                    Primary gap: {c.weak_areas.join(', ')}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-6 justify-between sm:justify-end border-t sm:border-t-0 border-slate-100 pt-3 sm:pt-0">
              <div className="text-right">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Readiness</span>
                <p
                  className={`text-xl font-black ${
                    c.readiness_score >= 80
                      ? 'text-emerald-600'
                      : c.readiness_score >= 65
                      ? 'text-amber-600'
                      : 'text-rose-600'
                  }`}
                >
                  {c.readiness_score}%
                </p>
              </div>

              <Link
                to={`/companies/${c.company_id}`}
                className="flex items-center gap-1 rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-brand-600 transition shadow-xs"
              >
                <span>View Details</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CompanyComparison;
