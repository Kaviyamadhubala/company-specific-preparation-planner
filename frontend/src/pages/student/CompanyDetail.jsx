import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import RoundTimeline from '../../components/common/RoundTimeline';
import {
  Building2,
  GraduationCap,
  Briefcase,
  GitBranch,
  ArrowRight,
  Award,
  Clock,
  Sparkles,
  ExternalLink,
  ShieldAlert
} from 'lucide-react';

const CompanyDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState(null);
  const [selectedRoleIndex, setSelectedRoleIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanyDetail();
  }, [id]);

  const fetchCompanyDetail = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/companies/${id}`);
      setCompany(res.data);
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

  if (!company) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center text-slate-500">
        <p>Company information not found.</p>
        <Link to="/companies" className="mt-4 inline-block text-xs font-bold text-brand-600">
          Back to Companies
        </Link>
      </div>
    );
  }

  const activeRole = company.roles?.[selectedRoleIndex] || company.roles?.[0];

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div
              className="flex h-20 w-20 shrink-0 items-center justify-center rounded-3xl text-white font-black text-2xl shadow-md"
              style={{ backgroundColor: company.logo_color || '#4f46e5' }}
            >
              {company.logo_initials || company.name.slice(0, 3).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                  {company.name}
                </h1>
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 capitalize">
                  {company.difficulty} Difficulty
                </span>
              </div>
              <p className="text-xs font-semibold text-brand-600 mt-1">{company.industry}</p>
              {company.website && (
                <a
                  href={company.website}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-600"
                >
                  <span>{company.website}</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
          </div>

          {activeRole && (
            <div className="flex flex-wrap items-center gap-3">
              <Link
                to={`/skill-gap?companyId=${company.id}&roleId=${activeRole.id}`}
                className="flex items-center gap-1.5 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-xs font-bold text-slate-700 hover:bg-slate-50 transition shadow-xs"
              >
                <span>Check Skill Gaps</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to={`/roadmap?companyId=${company.id}&roleId=${activeRole.id}`}
                className="flex items-center gap-1.5 rounded-2xl bg-brand-600 px-5 py-3 text-xs font-bold text-white shadow-lg shadow-brand-500/25 hover:bg-brand-700 transition"
              >
                <GitBranch className="h-4 w-4" />
                <span>Generate Prep Roadmap</span>
              </Link>
            </div>
          )}
        </div>

        {/* Company Description & Eligibility */}
        <div className="mt-6 pt-6 border-t border-slate-100 grid gap-6 md:grid-cols-2">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
              About the Company
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">{company.description}</p>
          </div>

          <div className="rounded-2xl bg-brand-50/50 p-4 border border-brand-100">
            <h3 className="text-xs font-bold uppercase tracking-wider text-brand-700 mb-1 flex items-center gap-1.5">
              <GraduationCap className="h-4 w-4" /> Eligibility Criteria & Cutoffs
            </h3>
            <p className="text-xs text-slate-700 leading-relaxed font-medium">
              {company.eligibility_notes || `Minimum ${company.min_cgpa || 6.0} CGPA in Graduation. All technical streams eligible.`}
            </p>
            <p className="mt-1 text-[11px] text-brand-600">
              Cutoff CGPA: <span className="font-extrabold">{company.min_cgpa || 6.0} / 10</span>
            </p>
          </div>
        </div>
      </div>

      {/* Target Role Selector */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Briefcase className="h-5 w-5 text-brand-600" />
            <h2 className="text-lg font-bold text-slate-900">Target Role Selection</h2>
          </div>
          <span className="text-xs text-slate-400">Select role to view specific skill expectations</span>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {company.roles?.map((r, idx) => (
            <button
              key={r.id}
              onClick={() => setSelectedRoleIndex(idx)}
              className={`rounded-2xl px-4 py-2.5 text-xs font-bold transition ${
                selectedRoleIndex === idx
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {r.role_name}
            </button>
          ))}
        </div>

        {/* Required Skills for the Selected Role */}
        {activeRole && (
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Required Skills for {activeRole.role_name}
            </h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {activeRole.skills?.map((s) => (
                <div
                  key={s.skill_id}
                  className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/60 p-3.5"
                >
                  <div>
                    <p className="text-xs font-extrabold text-slate-900">{s.skill_name}</p>
                    <p className="text-[10px] text-slate-400 uppercase">{s.skill_category}</p>
                  </div>
                  <span className="rounded-lg bg-indigo-100 px-2 py-1 text-[11px] font-bold text-indigo-700">
                    {s.required_level_label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recruitment Process Timeline */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Recruitment Process & Selection Timeline</h2>
            <p className="text-xs text-slate-500">
              Expected stages, evaluation categories, and difficulty of each selection round
            </p>
          </div>
          <span className="text-xs font-bold text-slate-400">
            {company.rounds?.length || 5} Consecutive Rounds
          </span>
        </div>

        <RoundTimeline rounds={company.rounds} />
      </div>

      {/* Action Footer Callout */}
      <div className="rounded-3xl bg-gradient-to-r from-brand-600 to-indigo-600 p-8 text-white shadow-lg shadow-brand-500/20 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <h3 className="text-xl font-black">Ready to prepare specifically for {company.name}?</h3>
          <p className="text-xs text-indigo-100 mt-1 max-w-xl">
            Our recommendation engine will compare your profile with {activeRole?.role_name || 'Software Developer'} requirements
            and build a daily roadmap with practice tests and mock interviews.
          </p>
        </div>

        <Link
          to={`/roadmap?companyId=${company.id}&roleId=${activeRole?.id}`}
          className="rounded-2xl bg-white px-6 py-3.5 text-xs font-extrabold text-brand-600 shadow-md hover:bg-slate-50 transition shrink-0"
        >
          Generate Preparation Roadmap Now
        </Link>
      </div>
    </div>
  );
};

export default CompanyDetail;
