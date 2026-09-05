import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { Sliders, Save, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';

const AdminWeights = () => {
  const [weights, setWeights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchWeights();
  }, []);

  const fetchWeights = async () => {
    try {
      setLoading(true);
      const res = await api.get('/admin/weights');
      setWeights(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleWeightChange = (category, val) => {
    setWeights((prev) =>
      prev.map((w) => (w.category === category ? { ...w, weight_pct: parseFloat(val) || 0 } : w))
    );
  };

  const total = weights.reduce((acc, curr) => acc + (curr.weight_pct || 0), 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');
    try {
      await api.put('/admin/weights', weights);
      setSuccess('Readiness scoring weights updated successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (e) {
      console.error(e);
      alert('Error updating weights.');
    } finally {
      setSaving(false);
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
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-slate-900 text-white px-3 py-1 text-xs font-bold mb-2">
          <Sliders className="h-3.5 w-3.5 text-brand-400" /> Mathematical Engine Configuration
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Configure Readiness Scoring Weights
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Adjust the weighted scoring algorithm used to calculate student placement readiness percentages
        </p>
      </div>

      {success && (
        <div className="flex items-center gap-2 rounded-2xl bg-emerald-50 p-4 text-xs font-semibold text-emerald-700 border border-emerald-200">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-900">Category Importance Sliders</h2>
            <p className="text-xs text-slate-400">Total weight should sum to 100%</p>
          </div>
          <div
            className={`text-sm font-black px-3 py-1 rounded-full ${
              Math.round(total) === 100
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-amber-100 text-amber-700'
            }`}
          >
            Total: {Math.round(total)}%
          </div>
        </div>

        <div className="space-y-5">
          {weights.map((w) => (
            <div key={w.category} className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-slate-900 capitalize">
                    {w.category.replace('_', ' ')}
                  </span>
                  <span className="text-slate-400 ml-2">({w.description})</span>
                </div>
                <div className="flex items-center gap-1">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    value={w.weight_pct}
                    onChange={(e) => handleWeightChange(w.category, e.target.value)}
                    className="w-16 rounded-xl border border-slate-200 px-2 py-1 text-right text-xs font-bold text-slate-900 focus:border-brand-500 focus:outline-none"
                  />
                  <span className="text-slate-500 font-bold">%</span>
                </div>
              </div>

              <input
                type="range"
                min="0"
                max="60"
                step="1"
                value={w.weight_pct}
                onChange={(e) => handleWeightChange(w.category, e.target.value)}
                className="w-full accent-brand-600 h-2 bg-slate-100 rounded-lg cursor-pointer"
              />
            </div>
          ))}
        </div>

        <div className="pt-6 border-t border-slate-100 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 rounded-2xl bg-brand-600 px-6 py-3 text-xs font-bold text-white shadow-md shadow-brand-500/25 hover:bg-brand-700 disabled:opacity-50 transition"
          >
            <Save className="h-4 w-4" />
            <span>{saving ? 'Updating Algorithm...' : 'Save Scoring Weights'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default AdminWeights;
