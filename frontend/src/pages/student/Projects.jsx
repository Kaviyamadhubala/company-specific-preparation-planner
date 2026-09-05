import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import {
  FolderGit2,
  Sparkles,
  Clock,
  Layers,
  ArrowRight,
  CheckCircle2,
  BookmarkPlus,
  ExternalLink
} from 'lucide-react';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [savedProjectIds, setSavedProjectIds] = useState(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const [recRes, myRes] = await Promise.all([
        api.get('/projects/recommendations'),
        api.get('/projects/my').catch(() => ({ data: [] }))
      ]);
      setProjects(recRes.data || []);
      const saved = new Set(myRes.data?.map((sp) => sp.project_id) || []);
      setSavedProjectIds(saved);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProject = async (projectId) => {
    try {
      await api.post(`/projects/${projectId}/save`);
      setSavedProjectIds((prev) => new Set([...prev, projectId]));
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
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-bold text-brand-700 mb-2">
          <Sparkles className="h-3.5 w-3.5" /> Portfolio Recommendation Engine
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Recommended Portfolio Projects
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Projects specifically selected to plug your active skill gaps and impress technical recruiters
        </p>
      </div>

      {/* Projects Grid */}
      <div className="grid gap-6 sm:grid-cols-2">
        {projects.map((p) => {
          const isSaved = savedProjectIds.has(p.id);
          return (
            <div
              key={p.id}
              className="rounded-3xl border border-slate-200/80 bg-white p-6 sm:p-7 shadow-xs flex flex-col justify-between transition hover:shadow-md"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between gap-3">
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border ${
                      p.difficulty === 'hard'
                        ? 'bg-rose-50 text-rose-700 border-rose-200'
                        : p.difficulty === 'medium'
                        ? 'bg-amber-50 text-amber-700 border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}
                  >
                    {p.difficulty} Difficulty
                  </span>
                  <span className="inline-flex items-center gap-1 text-xs text-slate-400 font-medium">
                    <Clock className="h-3.5 w-3.5" /> {p.duration_days} days
                  </span>
                </div>

                <div>
                  <h3 className="text-lg font-black text-slate-900 tracking-tight">{p.title}</h3>
                  <p className="mt-2 text-xs text-slate-600 leading-relaxed">{p.why_it_helps}</p>
                </div>

                <div className="rounded-2xl bg-slate-50 p-3.5 border border-slate-100 space-y-1 text-xs">
                  <p className="font-bold text-slate-700">Skills Demonstrated:</p>
                  <p className="text-brand-600 font-semibold">{p.skills_covered}</p>
                  <p className="text-[11px] text-slate-400 pt-1">
                    Tech Stack: <span className="text-slate-600">{p.technologies}</span>
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => handleSaveProject(p.id)}
                  disabled={isSaved}
                  className={`flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-bold transition ${
                    isSaved
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {isSaved ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                      <span>Added to Plan</span>
                    </>
                  ) : (
                    <>
                      <BookmarkPlus className="h-3.5 w-3.5" />
                      <span>Add to Prep List</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Projects;
