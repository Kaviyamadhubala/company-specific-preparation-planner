import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../../services/api';
import {
  GitBranch,
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Building2,
  Briefcase,
  Layers,
  ChevronDown,
  ChevronUp,
  RefreshCw
} from 'lucide-react';

const Roadmap = () => {
  const [searchParams] = useSearchParams();
  const [companies, setCompanies] = useState([]);
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [openWeek, setOpenWeek] = useState(1);

  // Form state for generating a new roadmap
  const [companyId, setCompanyId] = useState(searchParams.get('companyId') || '');
  const [roleId, setRoleId] = useState(searchParams.get('roleId') || '1');
  const [totalDays, setTotalDays] = useState(30);
  const [dailyHours, setDailyHours] = useState(2.5);

  useEffect(() => {
    fetchInitial();
  }, []);

  const fetchInitial = async () => {
    try {
      setLoading(true);
      const [compRes, currentRoadmapRes] = await Promise.all([
        api.get('/companies'),
        api.get('/roadmap/current').catch(() => ({ data: null }))
      ]);
      setCompanies(compRes.data);
      if (compRes.data.length > 0 && !companyId) {
        setCompanyId(compRes.data[0].id);
      }
      if (currentRoadmapRes.data) {
        setRoadmap(currentRoadmapRes.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const res = await api.post('/roadmap/generate', {
        company_id: parseInt(companyId),
        company_role_id: parseInt(roleId),
        total_days: parseInt(totalDays),
        daily_hours: parseFloat(dailyHours)
      });
      setRoadmap(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleTask = async (taskId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
      await api.put(`/roadmap/tasks/${taskId}`, { status: newStatus });
      // Update local state
      setRoadmap((prev) => {
        if (!prev) return prev;
        const newWeeks = prev.weeks.map((w) => ({
          ...w,
          tasks: w.tasks.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
        }));
        // Recompute completion
        let total = 0;
        let done = 0;
        newWeeks.forEach((w) => {
          total += w.tasks.length;
          done += w.tasks.filter((t) => t.status === 'completed').length;
        });
        const completion_pct = total > 0 ? Math.round((done / total) * 100) : 0;
        return { ...prev, weeks: newWeeks, completion_pct };
      });
    } catch (e) {
      console.error(e);
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
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-bold text-brand-700 mb-2">
          <Sparkles className="h-3.5 w-3.5" /> Adaptive Roadmap Engine
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Personalized Preparation Roadmap
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Custom schedule allocating study hours strictly according to your skill gaps and target company rounds
        </p>
      </div>

      {/* Generator Configuration Panel */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-xs">
        <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
          <RefreshCw className="h-4 w-4 text-brand-600" /> Roadmap Generation Parameters
        </h2>

        <form onSubmit={handleGenerate} className="grid gap-4 sm:grid-cols-2 md:grid-cols-4 items-end">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
              Target Company
            </label>
            <select
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-900 focus:border-brand-500 focus:outline-none"
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
              Target Role
            </label>
            <select
              value={roleId}
              onChange={(e) => setRoleId(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-900 focus:border-brand-500 focus:outline-none"
            >
              <option value="1">Software Developer</option>
              <option value="2">Software Engineer</option>
              <option value="3">Java Developer</option>
              <option value="4">Backend Developer</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
              Preparation Duration
            </label>
            <select
              value={totalDays}
              onChange={(e) => setTotalDays(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-900 focus:border-brand-500 focus:outline-none"
            >
              <option value="15">15 Days (Crash Course)</option>
              <option value="30">30 Days (Recommended)</option>
              <option value="45">45 Days (Comprehensive)</option>
              <option value="60">60 Days (In-Depth Mastery)</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={generating}
              className="w-full rounded-2xl bg-brand-600 py-3 text-xs font-bold text-white shadow-md shadow-brand-500/25 hover:bg-brand-700 disabled:opacity-50 transition"
            >
              {generating ? 'Generating Schedule...' : 'Generate New Roadmap'}
            </button>
          </div>
        </form>
      </div>

      {roadmap && (
        <div className="space-y-6">
          {/* Active Roadmap Banner */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-200">
                  Active Roadmap
                </span>
                <span className="text-xs text-slate-400 font-medium">
                  {roadmap.total_days} Days &bull; {roadmap.daily_hours} hrs/day
                </span>
              </div>
              <h2 className="mt-2 text-xl sm:text-2xl font-black text-slate-900">
                {roadmap.company_name} — {roadmap.role_name}
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Started {new Date(roadmap.start_date).toLocaleDateString()} &bull; Target completion:{' '}
                {new Date(roadmap.end_date).toLocaleDateString()}
              </p>
            </div>

            <div className="w-full md:w-64 space-y-2">
              <div className="flex justify-between text-xs font-bold text-slate-700">
                <span>Overall Completion</span>
                <span className="text-brand-600">{roadmap.completion_pct}%</span>
              </div>
              <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-brand-600 transition-all duration-700"
                  style={{ width: `${roadmap.completion_pct}%` }}
                />
              </div>
            </div>
          </div>

          {/* Adaptive Notice alert */}
          <div className="rounded-2xl border border-indigo-100 bg-indigo-50/50 p-4 text-xs text-indigo-900 flex items-start gap-3">
            <Sparkles className="h-4 w-4 text-brand-600 shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              <span className="font-bold">Adaptive Feedback Active: </span>
              If your score drops below 60% on practice tests, the system automatically inserts prerequisite
              revision tasks. Scoring above 85% fast-tracks you to advanced topics!
            </p>
          </div>

          {/* Weeks Accordion */}
          <div className="space-y-4">
            {roadmap.weeks?.map((w) => {
              const isOpen = openWeek === w.week_number;
              const weekCompleted = w.tasks.filter((t) => t.status === 'completed').length;
              return (
                <div
                  key={w.id}
                  className="rounded-3xl border border-slate-200 bg-white overflow-hidden shadow-xs transition"
                >
                  <button
                    onClick={() => setOpenWeek(isOpen ? null : w.week_number)}
                    className="w-full p-6 flex items-center justify-between text-left hover:bg-slate-50/50 transition"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 font-extrabold text-sm border border-brand-200">
                        W{w.week_number}
                      </div>
                      <div>
                        <h3 className="font-extrabold text-slate-900 text-base">{w.theme}</h3>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {weekCompleted} of {w.tasks.length} tasks completed
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <span className="text-xs font-bold text-brand-600 hidden sm:inline">
                        {Math.round((weekCompleted / (w.tasks.length || 1)) * 100)}%
                      </span>
                      {isOpen ? (
                        <ChevronUp className="h-5 w-5 text-slate-400" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-slate-400" />
                      )}
                    </div>
                  </button>

                  {isOpen && (
                    <div className="border-t border-slate-100 p-6 pt-2 divide-y divide-slate-100 bg-slate-50/30">
                      {w.tasks?.map((t) => (
                        <div
                          key={t.id}
                          className="py-3.5 flex items-center justify-between gap-4 hover:bg-white rounded-xl px-2 transition"
                        >
                          <div className="flex items-center gap-3">
                            <button
                              onClick={() => handleToggleTask(t.id, t.status)}
                              className={`h-5 w-5 shrink-0 rounded-md border flex items-center justify-center transition ${
                                t.status === 'completed'
                                  ? 'border-brand-600 bg-brand-600 text-white'
                                  : 'border-slate-300 hover:border-brand-500'
                              }`}
                            >
                              {t.status === 'completed' && <CheckCircle2 className="h-3.5 w-3.5" />}
                            </button>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-[11px] font-bold text-slate-400">Day {t.day_number}</span>
                                <span
                                  className={`text-sm font-semibold text-slate-800 ${
                                    t.status === 'completed' ? 'line-through text-slate-400' : ''
                                  }`}
                                >
                                  {t.title}
                                </span>
                              </div>
                              {t.description && (
                                <p className="text-xs text-slate-500 mt-0.5">{t.description}</p>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center gap-3 text-xs text-slate-400 shrink-0">
                            <span className="hidden sm:inline-flex items-center gap-1">
                              <Clock className="h-3.5 w-3.5" /> {t.estimated_minutes} min
                            </span>
                            <span className="capitalize text-[10px] font-bold bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                              {t.difficulty}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default Roadmap;
