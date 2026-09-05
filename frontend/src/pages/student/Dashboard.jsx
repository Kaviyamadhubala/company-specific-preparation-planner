import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import ReadinessCard from '../../components/common/ReadinessCard';
import { WeeklyProgressChart } from '../../components/charts/ProgressCharts';
import {
  GitBranch,
  CheckCircle2,
  HelpCircle,
  MessageSquare,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Calendar,
  Clock,
  ExternalLink,
  BookOpen,
  FolderGit2
} from 'lucide-react';

const Dashboard = () => {
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [todayTasks, setTodayTasks] = useState([]);
  const [recommendedProjects, setRecommendedProjects] = useState([]);
  const [resources, setResources] = useState([]);
  const [weeklyData, setWeeklyData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [pRes, progRes, tasksRes, projRes, resRes, wkRes] = await Promise.all([
        api.get('/students/profile').catch(() => ({ data: null })),
        api.get('/progress').catch(() => ({ data: null })),
        api.get('/roadmap/tasks/today').catch(() => ({ data: [] })),
        api.get('/projects/recommendations').catch(() => ({ data: [] })),
        api.get('/recommendations/resources?topic=DSA').catch(() => ({ data: [] })),
        api.get('/progress/weekly').catch(() => ({ data: [] }))
      ]);

      setProfile(pRes.data);
      setProgress(progRes.data);
      setTodayTasks(tasksRes.data || []);
      setRecommendedProjects(projRes.data || []);
      setResources(resRes.data?.slice(0, 3) || []);
      setWeeklyData(wkRes.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (taskId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
      await api.put(`/roadmap/tasks/${taskId}`, { status: newStatus });
      setTodayTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      // Refresh progress stats
      const progRes = await api.get('/progress');
      setProgress(progRes.data);
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

  const targetCompany = progress?.current_company || 'TCS';
  const targetRole = progress?.current_role || 'Software Developer';
  const readiness = progress?.readiness_score || 78;
  const roadmapPct = progress?.roadmap_completion_pct || 64;
  const practiceAvg = progress?.practice_avg_score || 82;
  const interviewAvg = progress?.mock_interview_avg_score || 76;

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-brand-900 p-8 text-white shadow-md">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold backdrop-blur text-brand-200">
              <Sparkles className="h-3.5 w-3.5" /> Placement Season Preparation
            </div>
            <h1 className="mt-3 text-2xl sm:text-3xl font-black tracking-tight">
              Welcome back, {profile?.full_name || 'Alex'}!
            </h1>
            <p className="mt-1 text-sm text-slate-300 max-w-xl">
              Targeting <span className="font-bold text-white">{targetCompany}</span> as a{' '}
              <span className="font-bold text-white">{targetRole}</span>. Keep up your daily momentum!
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link
              to="/companies"
              className="rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 px-4 py-2.5 text-xs font-bold text-white backdrop-blur transition"
            >
              Switch Target Company
            </Link>
            <Link
              to="/roadmap"
              className="rounded-xl bg-brand-500 hover:bg-brand-600 px-4 py-2.5 text-xs font-bold text-white shadow-md transition flex items-center gap-1.5"
            >
              <GitBranch className="h-4 w-4" /> View Full Roadmap
            </Link>
          </div>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Company Readiness</span>
            <span className="text-brand-600">Weighted</span>
          </div>
          <p className="mt-2 text-3xl font-black text-slate-900">{readiness}%</p>
          <div className="mt-2 flex items-center text-xs text-slate-400">
            <span>Target: 85% &bull; Gap: {Math.max(0, 85 - readiness)}%</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Roadmap Completion</span>
            <span className="text-indigo-600">Progress</span>
          </div>
          <p className="mt-2 text-3xl font-black text-slate-900">{roadmapPct}%</p>
          <div className="mt-2 flex items-center text-xs text-slate-400">
            <span>{progress?.tasks_completed || 0} / {progress?.tasks_total || 0} tasks done</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Practice Average</span>
            <span className="text-emerald-600">Tests</span>
          </div>
          <p className="mt-2 text-3xl font-black text-slate-900">{practiceAvg}%</p>
          <div className="mt-2 flex items-center text-xs text-slate-400">
            <span>{progress?.tests_taken || 0} practice sessions submitted</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Mock Interview Score</span>
            <span className="text-amber-600">AI Evaluation</span>
          </div>
          <p className="mt-2 text-3xl font-black text-slate-900">{interviewAvg}%</p>
          <div className="mt-2 flex items-center text-xs text-slate-400">
            <span>Technical & clarity rating</span>
          </div>
        </div>
      </div>

      {/* Readiness Engine Card + Weak Areas */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ReadinessCard
            score={readiness}
            companyName={targetCompany}
            roleName={targetRole}
            isEligible={true}
            eligibilityNote="Meets standard academic criteria (60%+ / 6.0 CGPA)"
          />
        </div>

        {/* Top Weak Areas widget */}
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-rose-600 mb-3">
              <AlertTriangle className="h-5 w-5" />
              <h3 className="font-bold text-slate-900 text-sm">Top Weak Areas Identified</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Derived from your skill levels and {targetCompany} expectations. Address these to maximize selection odds:
            </p>

            <div className="space-y-2.5">
              {[
                { name: 'DSA (Trees & Dynamic Programming)', gap: 'Major Gap', color: 'bg-rose-50 text-rose-700 border-rose-200' },
                { name: 'Technical Interview Self-Defense', gap: 'Needs Improvement', color: 'bg-amber-50 text-amber-700 border-amber-200' },
                { name: 'OOP Design Patterns (SOLID)', gap: 'Needs Improvement', color: 'bg-amber-50 text-amber-700 border-amber-200' }
              ].map((wa, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/50 p-3 text-xs">
                  <span className="font-semibold text-slate-800">{wa.name}</span>
                  <span className={`px-2 py-0.5 rounded-full border text-[10px] font-bold ${wa.color}`}>
                    {wa.gap}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <Link
            to="/skill-gap"
            className="mt-5 flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white py-2 text-xs font-bold text-slate-700 hover:bg-slate-50 transition"
          >
            <span>Analyze All Skill Gaps</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>

      {/* Today's Preparation Tasks */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-brand-600" />
              <h3 className="text-lg font-bold text-slate-900">Today's Preparation Tasks</h3>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Personalized for {targetCompany} &bull; Check tasks to update your readiness score
            </p>
          </div>

          <Link
            to="/tasks"
            className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1"
          >
            <span>View All Daily Tasks</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {todayTasks.length === 0 ? (
          <p className="text-center py-8 text-sm text-slate-400">
            No pending tasks for today. Explore the roadmap or start a practice test!
          </p>
        ) : (
          <div className="divide-y divide-slate-100">
            {todayTasks.map((t) => (
              <div
                key={t.id}
                className="py-3.5 flex items-center justify-between gap-4 hover:bg-slate-50/60 rounded-xl px-2 transition"
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
                    <p
                      className={`text-sm font-semibold text-slate-800 ${
                        t.status === 'completed' ? 'line-through text-slate-400' : ''
                      }`}
                    >
                      {t.title}
                    </p>
                    <p className="text-xs text-slate-500">{t.description}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-400 shrink-0">
                  <span className="hidden sm:inline-flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" /> {t.estimated_minutes} min
                  </span>
                  <span className="capitalize text-[11px] font-medium bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                    {t.difficulty}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Charts & Learning Recommendations */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Weekly Preparation Trend */}
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Preparation Velocity</h3>
              <p className="text-xs text-slate-500">Weekly test performance trend</p>
            </div>
            <Link to="/progress" className="text-xs font-semibold text-brand-600 hover:text-brand-700">
              Analytics
            </Link>
          </div>
          <WeeklyProgressChart data={weeklyData} />
        </div>

        {/* Recommended Projects */}
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Recommended Projects</h3>
                <p className="text-xs text-slate-500">Targeted to plug your active skill gaps</p>
              </div>
              <Link to="/projects" className="text-xs font-semibold text-brand-600 hover:text-brand-700">
                Browse All
              </Link>
            </div>

            <div className="space-y-3">
              {recommendedProjects.slice(0, 3).map((p) => (
                <div key={p.id} className="rounded-2xl border border-slate-100 bg-slate-50/50 p-4">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-bold text-xs text-slate-900">{p.title}</h4>
                    <span className="text-[10px] font-semibold text-brand-600 bg-brand-50 px-2 py-0.5 rounded">
                      {p.duration_days} days
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-2">{p.why_it_helps}</p>
                  <p className="mt-2 text-[10px] font-medium text-slate-400">
                    Tech: {p.technologies}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
