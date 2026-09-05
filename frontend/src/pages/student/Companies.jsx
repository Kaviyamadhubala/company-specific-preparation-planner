import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { Building2, Search, ArrowRight, Star, Award, ShieldCheck, Filter } from 'lucide-react';

const Companies = () => {
  const [companies, setCompanies] = useState([]);
  const [search, setSearch] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const res = await api.get('/companies');
      setCompanies(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filteredCompanies = companies.filter((c) => {
    const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.industry && c.industry.toLowerCase().includes(search.toLowerCase()));
    const matchesDiff = difficultyFilter === 'all' || c.difficulty === difficultyFilter;
    return matchesSearch && matchesDiff;
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Select Target Company
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Choose a recruiter to inspect their recruitment pipeline and generate a custom preparation roadmap
          </p>
        </div>

        <Link
          to="/compare"
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50 shadow-xs transition"
        >
          <span>Compare All Companies</span>
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by company name or industry (e.g. TCS, Zoho, SaaS)..."
            className="w-full rounded-2xl border border-slate-200 bg-white pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400 shrink-0" />
          <select
            value={difficultyFilter}
            onChange={(e) => setDifficultyFilter(e.target.value)}
            className="rounded-2xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-700 focus:border-brand-500 focus:outline-none"
          >
            <option value="all">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
      </div>

      {/* Companies Grid */}
      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
        </div>
      ) : filteredCompanies.length === 0 ? (
        <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center text-slate-400">
          <Building2 className="mx-auto h-12 w-12 text-slate-300" />
          <p className="mt-3 text-sm font-semibold">No companies match your filters</p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredCompanies.map((c) => (
            <div
              key={c.id}
              className="group relative flex flex-col justify-between rounded-3xl border border-slate-200/80 bg-white p-6 shadow-xs transition hover:-translate-y-0.5 hover:shadow-lg"
            >
              <div>
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div
                    className="flex h-14 w-14 items-center justify-center rounded-2xl text-white font-black text-lg shadow-md"
                    style={{ backgroundColor: c.logo_color || '#4f46e5' }}
                  >
                    {c.logo_initials || c.name.slice(0, 3).toUpperCase()}
                  </div>

                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border ${
                      c.difficulty === 'hard'
                        ? 'bg-rose-50 text-rose-700 border-rose-200'
                        : c.difficulty === 'medium'
                        ? 'bg-amber-50 text-amber-700 border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}
                  >
                    {c.difficulty} Difficulty
                  </span>
                </div>

                <h3 className="text-xl font-black text-slate-900 tracking-tight group-hover:text-brand-600 transition">
                  {c.name}
                </h3>
                <p className="text-xs font-semibold text-brand-600 mt-0.5">{c.industry}</p>

                <p className="mt-2.5 text-xs text-slate-500 line-clamp-2 leading-relaxed">
                  {c.description || 'Global technology firm with structured campus hiring.'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <div className="text-[11px] text-slate-500">
                  <span className="font-bold text-slate-700">{c.role_count || 2}</span> Roles &bull;{' '}
                  <span>Min {c.min_cgpa || 6.0} CGPA</span>
                </div>

                <Link
                  to={`/companies/${c.id}`}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-bold text-white transition hover:bg-brand-600"
                >
                  <span>Explore</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Companies;
