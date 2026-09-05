import React from 'react';
import { Link } from 'react-router-dom';
import {
  Compass,
  ArrowRight,
  CheckCircle2,
  GitBranch,
  Target,
  BrainCircuit,
  BarChart3,
  ShieldCheck,
  Building2,
  Sparkles
} from 'lucide-react';

const LandingPage = () => {
  const steps = [
    { title: 'Student Profile', desc: 'Input your academic credentials and current skill proficiency ratings.' },
    { title: 'Target Company & Role', desc: 'Pick from top tier companies (TCS, Infosys, Zoho, Accenture, etc.) and specific job roles.' },
    { title: 'Recruitment Analysis', desc: 'Inspect verified rounds, technical cutoffs, and required competency levels.' },
    { title: 'Skill Gap Engine', desc: 'Real-time mathematical gap identification categorizing skills as Ready, Needs Work, or Major Gap.' },
    { title: 'Personalized Roadmap', desc: 'A day-by-day customized study schedule with adaptive adjustments on test completion.' },
    { title: 'AI Mock Interview', desc: 'Interactive interview simulation with instant communication & technical feedback.' },
  ];

  const companies = [
    { name: 'TCS', color: '#0033A0', roles: 'Software Developer, Engineer' },
    { name: 'Infosys', color: '#007CC3', roles: 'Software Developer, Java Dev' },
    { name: 'Accenture', color: '#A100FF', roles: 'Software Engineer, Analyst' },
    { name: 'Zoho', color: '#E42527', roles: 'Backend, Product Developer' },
    { name: 'Wipro', color: '#341C6C', roles: 'Project Engineer, Developer' },
    { name: 'IBM', color: '#006699', roles: 'Software Engineer, Data Analyst' },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white shadow-md shadow-brand-500/20">
              <Compass className="h-6 w-6" />
            </div>
            <span className="text-xl font-black tracking-tight text-slate-900">
              Prep<span className="text-brand-600">Planner</span>
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="px-4 py-2 text-sm font-semibold text-slate-700 hover:text-slate-900 transition"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-brand-500/20 hover:bg-brand-700 transition"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 px-6 text-center max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-xs font-bold text-brand-700 mb-6 shadow-xs">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Intelligent Placement Preparation Engine</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-950 leading-[1.15]">
          Target Your Dream Company with a{' '}
          <span className="bg-gradient-to-r from-brand-600 to-indigo-500 bg-clip-text text-transparent">
            Precision Preparation Roadmap
          </span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
          Stop preparing randomly. Analyze company-specific recruitment rounds, identify exact skill gaps,
          and follow an adaptive day-by-day roadmap built specifically for you.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/register"
            className="flex w-full sm:w-auto items-center justify-center gap-2 rounded-2xl bg-brand-600 px-8 py-4 text-base font-bold text-white shadow-lg shadow-brand-500/30 hover:bg-brand-700 transition"
          >
            <span>Start My Preparation</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            to="/login"
            className="flex w-full sm:w-auto items-center justify-center gap-2 rounded-2xl border border-slate-300 bg-white px-8 py-4 text-base font-bold text-slate-700 hover:bg-slate-50 transition"
          >
            <span>Demo Student Login</span>
          </Link>
        </div>

        {/* Demo Credentials box */}
        <div className="mt-6 inline-block rounded-xl border border-slate-200 bg-white p-3 text-xs text-slate-500">
          <span className="font-bold text-slate-700">Sample Login: </span>
          <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-800">student@example.com</code> /{' '}
          <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-800">Student@123</code> &bull;{' '}
          <span className="font-bold text-slate-700">Admin: </span>
          <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-800">admin@prepplanner.com</code> /{' '}
          <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-800">Admin@123</code>
        </div>
      </section>

      {/* Workflow Process */}
      <section className="py-16 px-6 bg-white border-y border-slate-200/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="text-xs font-extrabold uppercase tracking-wider text-brand-600">The Core Flow</h2>
            <p className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900">
              From Student Profile to Company Readiness
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {steps.map((s, idx) => (
              <div
                key={idx}
                className="relative rounded-2xl border border-slate-200 bg-slate-50/50 p-6 transition hover:bg-white hover:shadow-md"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-600 text-white font-bold text-xs">
                    0{idx + 1}
                  </div>
                  <h3 className="font-bold text-slate-900 text-base">{s.title}</h3>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Target Companies */}
      <section className="py-16 px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-xs font-extrabold uppercase tracking-wider text-brand-600">Top Recruiters</h2>
          <p className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900">
            Tailored Roadmaps for Leading Tech Employers
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
          {companies.map((c) => (
            <div
              key={c.name}
              className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-xs"
            >
              <div
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-white font-black text-base shadow-sm"
                style={{ backgroundColor: c.color }}
              >
                {c.name.slice(0, 3)}
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-base">{c.name}</h4>
                <p className="text-xs text-slate-500">{c.roles}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-8 px-6 text-center text-xs text-slate-500">
        <p>&copy; {new Date().getFullYear()} PrepPlanner. All company patterns are configurable by administrators.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
