import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import {
  BarChart3,
  TrendingUp,
  Clock,
  Award,
  GitBranch,
  CheckCircle2,
  Calendar,
  Sparkles
} from 'lucide-react';
import { WeeklyProgressChart } from '../../components/charts/ProgressCharts';

const Progress = () => {
  const [progress, setProgress] = useState(null);
  const [weeklyData, setWeeklyData] = useState([]);
  const [skillProgress, setSkillProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      setLoading(true);
      const [pRes, wRes, sRes] = await Promise.all([
        api.get('/progress'),
        api.get('/progress/weekly'),
        api.get('/progress/skills').catch(() => ({ data: [] }))
      ]);
      setProgress(pRes.data);
      setWeeklyData(wRes.data || []);
      setSkillProgress(sRes.data || []);
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
          <Sparkles className="h-3.5 w-3.5" /> Performance Analytics
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Preparation Progress & Velocity Analytics
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Historical metrics tracking your roadmap milestones, practice tests, and competency growth
        </p>
      </div>

      {/* Top 4 Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase">
            <GitBranch className="h-4 w-4 text-brand-600" /> Roadmap Completion
          </div>
          <p className="mt-3 text-3xl font-black text-slate-900">
            {progress?.roadmap_completion_pct || 0}%
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {progress?.tasks_completed || 0} of {progress?.tasks_total || 0} tasks finished
          </p>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase">
            <Award className="h-4 w-4 text-emerald-600" /> Practice Average
          </div>
          <p className="mt-3 text-3xl font-black text-slate-900">
            {progress?.practice_avg_score || 0}%
          </p>
          <p className="mt-1 text-xs text-slate-500">Across {progress?.tests_taken || 0} assessments</p>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase">
            <TrendingUp className="h-4 w-4 text-amber-600" /> Mock Interview Rating
          </div>
          <p className="mt-3 text-3xl font-black text-slate-900">
            {progress?.mock_interview_avg_score || 76}%
          </p>
          <p className="mt-1 text-xs text-slate-500">AI communication & tech score</p>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase">
            <Clock className="h-4 w-4 text-indigo-600" /> Total Study Hours
          </div>
          <p className="mt-3 text-3xl font-black text-slate-900">
            {progress?.total_study_hours || 0} hrs
          </p>
          <p className="mt-1 text-xs text-slate-500">Logged preparation time</p>
        </div>
      </div>

      {/* Velocity Trend Chart */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-bold text-slate-900">Weekly Score Trend</h2>
            <p className="text-xs text-slate-500">Assessment accuracy across study weeks</p>
          </div>
          <span className="text-xs font-semibold text-brand-600">Active Cycle</span>
        </div>
        <WeeklyProgressChart data={weeklyData} />
      </div>

      {/* Skill Level Improvement Matrix */}
      {skillProgress.length > 0 && (
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
          <h2 className="text-base font-bold text-slate-900 mb-4">Competency Improvement Log</h2>
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
            {skillProgress.map((sp) => (
              <div
                key={sp.skill_name}
                className="rounded-2xl border border-slate-100 bg-slate-50/50 p-4 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-slate-900">{sp.skill_name}</span>
                  {sp.improvement > 0 ? (
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                      +{sp.improvement} Lvl
                    </span>
                  ) : (
                    <span className="text-[10px] text-slate-400 font-medium">Consistent</span>
                  )}
                </div>
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Initial: Level {sp.initial_level}</span>
                  <span className="font-bold text-slate-800">Current: Level {sp.current_level}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Progress;
