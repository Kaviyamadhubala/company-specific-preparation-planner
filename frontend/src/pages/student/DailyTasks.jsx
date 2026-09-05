import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import {
  CalendarCheck,
  CheckCircle2,
  Clock,
  Sparkles,
  Award,
  ArrowRight,
  Filter,
  Check,
  Building2
} from 'lucide-react';

const DailyTasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const [tRes, pRes] = await Promise.all([
        api.get('/roadmap/tasks/today'),
        api.get('/progress')
      ]);
      setTasks(tRes.data || []);
      setProgress(pRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (taskId, currentStatus) => {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      await api.put(`/roadmap/tasks/${taskId}`, { status: newStatus });
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
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

  const completedCount = tasks.filter((t) => t.status === 'completed').length;
  const targetCompany = progress?.current_company || 'TCS';

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-bold text-brand-700 mb-2">
            <CalendarCheck className="h-3.5 w-3.5" /> Daily Preparation Schedule
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Today's Target Tasks
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Target Company: <span className="font-bold text-slate-700">{targetCompany}</span> &bull;{' '}
            Complete each task to ensure comprehensive placement readiness
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 font-black text-base">
            {completedCount}/{tasks.length}
          </div>
          <div>
            <p className="text-xs font-bold text-slate-900">Today's Progress</p>
            <p className="text-[11px] text-slate-400">
              {tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0}% Complete
            </p>
          </div>
        </div>
      </div>

      {/* Task Checklist */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
          <h2 className="text-base font-bold text-slate-900">Action Items Checklist</h2>
          <span className="text-xs text-slate-400">Click circle to mark completed</span>
        </div>

        {tasks.length === 0 ? (
          <div className="py-12 text-center text-slate-400">
            <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-400 mb-3" />
            <p className="font-semibold text-slate-700">All tasks completed for today!</p>
            <p className="text-xs mt-1">Take a practice quiz or review interview questions to stay sharp.</p>
            <Link
              to="/practice"
              className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-brand-700 transition"
            >
              <span>Take a Practice Quiz</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((t) => {
              const isDone = t.status === 'completed';
              return (
                <div
                  key={t.id}
                  onClick={() => handleToggle(t.id, t.status)}
                  className={`cursor-pointer rounded-2xl border p-4.5 transition flex items-center justify-between gap-4 ${
                    isDone
                      ? 'border-emerald-200 bg-emerald-50/40 text-slate-500'
                      : 'border-slate-200/80 bg-white hover:border-brand-400 hover:shadow-xs'
                  }`}
                >
                  <div className="flex items-center gap-3.5">
                    <button
                      type="button"
                      className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-lg border transition ${
                        isDone
                          ? 'border-emerald-600 bg-emerald-600 text-white'
                          : 'border-slate-300 bg-white'
                      }`}
                    >
                      {isDone && <Check className="h-4 w-4" />}
                    </button>
                    <div>
                      <p className={`text-sm font-bold ${isDone ? 'line-through text-slate-400' : 'text-slate-900'}`}>
                        {t.title}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">{t.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-400 shrink-0">
                    <span className="hidden sm:inline-flex items-center gap-1 font-medium">
                      <Clock className="h-3.5 w-3.5" /> {t.estimated_minutes} min
                    </span>
                    <span className="capitalize text-[10px] font-bold bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                      {t.difficulty}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default DailyTasks;
