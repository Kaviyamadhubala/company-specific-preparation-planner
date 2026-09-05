import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import {
  Building2,
  Plus,
  Edit2,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Save,
  X
} from 'lucide-react';

const AdminCompanies = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCompany, setEditingCompany] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    logo_color: '#4f46e5',
    logo_initials: '',
    industry: 'IT Services',
    difficulty: 'medium',
    min_cgpa: 6.0,
    description: '',
    eligibility_notes: '',
    website: ''
  });

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

  const handleOpenModal = (comp = null) => {
    if (comp) {
      setEditingCompany(comp);
      setFormData({
        name: comp.name,
        logo_color: comp.logo_color || '#4f46e5',
        logo_initials: comp.logo_initials || comp.name.slice(0, 3).toUpperCase(),
        industry: comp.industry || 'IT Services',
        difficulty: comp.difficulty || 'medium',
        min_cgpa: comp.min_cgpa || 6.0,
        description: comp.description || '',
        eligibility_notes: comp.eligibility_notes || '',
        website: comp.website || ''
      });
    } else {
      setEditingCompany(null);
      setFormData({
        name: '',
        logo_color: '#4f46e5',
        logo_initials: '',
        industry: 'IT Services',
        difficulty: 'medium',
        min_cgpa: 6.0,
        description: '',
        eligibility_notes: '',
        website: ''
      });
    }
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCompany) {
        await api.put(`/admin/companies/${editingCompany.id}`, formData);
      } else {
        await api.post('/admin/companies', formData);
      }
      setShowModal(false);
      fetchCompanies();
    } catch (e) {
      console.error(e);
      alert('Failed to save company.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to deactivate this company?')) return;
    try {
      await api.delete(`/admin/companies/${id}`);
      fetchCompanies();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Manage Recruiter Companies & Rounds
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Recruitment patterns change over time — update cutoffs, eligibility criteria, and rounds
          </p>
        </div>

        <button
          onClick={() => handleOpenModal()}
          className="flex items-center gap-2 rounded-2xl bg-brand-600 px-5 py-3 text-xs font-bold text-white shadow-md shadow-brand-500/25 hover:bg-brand-700 transition shrink-0"
        >
          <Plus className="h-4 w-4" />
          <span>Add New Company</span>
        </button>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {companies.map((c) => (
            <div
              key={c.id}
              className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div
                    className="flex h-12 w-12 items-center justify-center rounded-2xl text-white font-black text-base shadow-sm"
                    style={{ backgroundColor: c.logo_color || '#4f46e5' }}
                  >
                    {c.logo_initials || c.name.slice(0, 3)}
                  </div>
                  <span className="capitalize text-[10px] font-bold bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                    {c.difficulty}
                  </span>
                </div>

                <h3 className="text-lg font-black text-slate-900">{c.name}</h3>
                <p className="text-xs font-semibold text-brand-600">{c.industry}</p>
                <p className="text-xs text-slate-500 mt-2 line-clamp-2">{c.description}</p>

                <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                  <span>Min CGPA: {c.min_cgpa}</span> &bull; <span>{c.role_count || 2} Roles</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  onClick={() => handleOpenModal(c)}
                  className="rounded-xl p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition"
                  title="Edit Company"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(c.id)}
                  className="rounded-xl p-2 text-rose-500 hover:bg-rose-50 transition"
                  title="Deactivate Company"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Add / Edit */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 overflow-y-auto">
          <div className="relative w-full max-w-lg rounded-3xl bg-white p-6 sm:p-8 shadow-2xl border border-slate-100">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
              <h3 className="text-lg font-bold text-slate-900">
                {editingCompany ? `Edit ${editingCompany.name}` : 'Add New Recruiter Company'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="rounded-full p-1 text-slate-400 hover:bg-slate-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-brand-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Initials (Logo)
                  </label>
                  <input
                    type="text"
                    maxLength={4}
                    value={formData.logo_initials}
                    onChange={(e) => setFormData({ ...formData, logo_initials: e.target.value })}
                    placeholder="TCS"
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-brand-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Industry
                  </label>
                  <input
                    type="text"
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-brand-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Difficulty Level
                  </label>
                  <select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-brand-500 focus:outline-none"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Cutoff Min CGPA
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  value={formData.min_cgpa}
                  onChange={(e) => setFormData({ ...formData, min_cgpa: parseFloat(e.target.value) })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Overview Description
                </label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Eligibility Notes
                </label>
                <textarea
                  rows={2}
                  value={formData.eligibility_notes}
                  onChange={(e) => setFormData({ ...formData, eligibility_notes: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-brand-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-brand-600 px-5 py-2 text-xs font-bold text-white hover:bg-brand-700 shadow-sm"
                >
                  Save Company
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminCompanies;
