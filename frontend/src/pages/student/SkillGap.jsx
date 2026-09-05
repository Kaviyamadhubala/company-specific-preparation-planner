import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../../services/api';
import SkillBadge from '../../components/common/SkillBadge';
import ReadinessCard from '../../components/common/ReadinessCard';
import { CategoryRadarChart, SkillGapBarChart } from '../../components/charts/ProgressCharts';
import {
  CheckSquare,
  AlertTriangle,
  GitBranch,
  Building2,
  Briefcase,
  ArrowRight,
  TrendingUp,
  Award,
  Layers
} from 'lucide-react';

const SkillGap = () => {
  const [searchParams] = useSearchParams();
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState(searchParams.get('companyId') || '');
  const [selectedRoleId, setSelectedRoleId] = useState(searchParams.get('roleId') || '');
  const [readinessData, setReadinessData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const res = await api.get('/companies');
      setCompanies(res.data);

      let compId = selectedCompanyId;
      let rId = selectedRoleId;

      if (!compId && res.data.length > 0) {
        compId = res.data[0].id;
        setSelectedCompanyId(compId);
      }

      if (compId) {
        const compDetail = await api.get(`/companies/${compId}`);
        if (!rId && compDetail.data.roles?.length > 0) {
          rId = compDetail.data.roles[0].id;
          setSelectedRoleId(rId);
        }
      }

      if (compId && rId) {
        fetchReadiness(compId, rId);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchReadiness = async (cId, rId) => {
    try {
      setLoading(true);
      const res = await api.get(`/readiness/${cId}/${rId}`);
      setReadinessData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanyChange = async (e) => {
    const cId = e.target.value;
    setSelectedCompanyId(cId);
    try {
      const compDetail = await api.get(`/companies/${cId}`);
      if (compDetail.data.roles?.length > 0) {
        const rId = compDetail.data.roles[0].id;
        setSelectedRoleId(rId);
        fetchReadiness(cId, rId);
      } else {
        setSelectedRoleId('');
        setReadinessData(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRoleChange = (e) => {
    const rId = e.target.value;
    setSelectedRoleId(rId);
    if (selectedCompanyId && rId) {
      fetchReadiness(selectedCompanyId, rId);
    }
  };

  const selectedCompanyObj = companies.find((c) => c.id === parseInt(selectedCompanyId));

  const radarData = readinessData?.breakdown?.map((b) => ({
    category: b.category.replace('_', ' ').toUpperCase(),
    score: b.score
  })) || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Skill Gap Analysis & Readiness Engine
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Real mathematical comparison between your current skill proficiencies and recruiter requirements
          </p>
        </div>

        {selectedCompanyId && selectedRoleId && (
          <Link
            to={`/roadmap?companyId=${selectedCompanyId}&roleId=${selectedRoleId}`}
            className="inline-flex items-center gap-2 rounded-2xl bg-brand-600 px-5 py-3 text-xs font-bold text-white shadow-lg shadow-brand-500/25 hover:bg-brand-700 transition"
          >
            <GitBranch className="h-4 w-4" />
            <span>Generate Targeted Roadmap</span>
          </Link>
        )}
      </div>

      {/* Selectors */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-xs grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1.5">
            <Building2 className="h-4 w-4 text-brand-600" /> Target Company
          </label>
          <select
            value={selectedCompanyId}
            onChange={handleCompanyChange}
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 focus:border-brand-500 focus:outline-none"
          >
            {companies.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.difficulty} difficulty)
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1.5">
            <Briefcase className="h-4 w-4 text-brand-600" /> Target Job Role
          </label>
          <select
            value={selectedRoleId}
            onChange={handleRoleChange}
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 focus:border-brand-500 focus:outline-none"
          >
            <option value="1">Software Developer</option>
            <option value="2">Software Engineer</option>
            <option value="3">Java Developer</option>
            <option value="4">Backend Developer</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
        </div>
      ) : readinessData ? (
        <div className="space-y-8">
          {/* Readiness Meter */}
          <ReadinessCard
            score={readinessData.overall_score}
            companyName={selectedCompanyObj?.name}
            roleName="Selected Profile"
            isEligible={readinessData.is_eligible}
            eligibilityNote={readinessData.eligibility_note}
          />

          {/* Category Breakdown & Radar Chart */}
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2 rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
              <div className="flex items-center gap-2 mb-4">
                <Layers className="h-5 w-5 text-brand-600" />
                <h3 className="text-base font-bold text-slate-900">
                  Weighted Category Breakdown
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-6">
                Calculated dynamically from configurable recruitment category weights
              </p>

              <div className="space-y-4">
                {readinessData.breakdown?.map((b) => (
                  <div key={b.category} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-slate-800 capitalize">
                        {b.category.replace('_', ' ')}
                      </span>
                      <span className="font-semibold text-slate-600">
                        {b.score}% &bull; Weight: {b.weight}%
                      </span>
                    </div>
                    <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          width: `${Math.min(b.score, 100)}%`,
                          backgroundColor:
                            b.score >= 80 ? '#10b981' : b.score >= 60 ? '#f59e0b' : '#ef4444'
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Radar Mastery */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 mb-1">Mastery Footprint</h3>
                <p className="text-xs text-slate-500 mb-4">Relative multi-axis competency</p>
                <CategoryRadarChart data={radarData} />
              </div>
            </div>
          </div>

          {/* Per-Skill Gap Visual Comparison Table */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Individual Skill Gap Matrix</h2>
              <p className="text-xs text-slate-500">
                Your current proficiency vs target requirement (Levels 0: Not Started &rarr; 5: Expert)
              </p>
            </div>

            <SkillGapBarChart data={readinessData.skill_gaps} />

            <div className="divide-y divide-slate-100 mt-6">
              {readinessData.skill_gaps?.map((g) => (
                <div
                  key={g.skill_id}
                  className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2.5">
                      <span className="font-extrabold text-slate-900 text-sm">{g.skill_name}</span>
                      <SkillBadge status={g.status} />
                    </div>
                    <p className="text-xs text-slate-500">
                      Category: <span className="capitalize">{g.skill_category}</span> &bull;{' '}
                      Your Level: <span className="font-bold text-slate-700">{g.student_level_label}</span> (
                      {g.student_level}/5) &bull; Required:{' '}
                      <span className="font-bold text-slate-700">{g.required_level_label}</span> (
                      {g.required_level}/5)
                    </p>
                  </div>

                  <div className="w-full sm:w-48 space-y-1">
                    <div className="flex justify-between text-xs font-semibold text-slate-600">
                      <span>Match</span>
                      <span>{g.percentage}%</span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${Math.min(g.percentage, 100)}%`,
                          backgroundColor:
                            g.status === 'ready'
                              ? '#10b981'
                              : g.status === 'needs_improvement'
                              ? '#f59e0b'
                              : '#ef4444'
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SkillGap;
