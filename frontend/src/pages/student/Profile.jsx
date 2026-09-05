import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { User, GraduationCap, MapPin, Phone, Clock, Briefcase, Award, Save, CheckCircle2, AlertCircle } from 'lucide-react';

const Profile = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    college: '',
    degree: '',
    branch: '',
    graduation_year: 2025,
    cgpa: 8.0,
    phone: '',
    location: '',
    daily_hours: 2.5,
    preferred_role: 'Software Developer',
    preferred_location: 'Bangalore',
    bio: ''
  });
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const [pRes, sRes] = await Promise.all([
        api.get('/students/profile'),
        api.get('/students/skills')
      ]);
      if (pRes.data) {
        setFormData({
          full_name: pRes.data.full_name || '',
          email: pRes.data.email || '',
          college: pRes.data.college || '',
          degree: pRes.data.degree || 'B.Tech',
          branch: pRes.data.branch || 'CSE',
          graduation_year: pRes.data.graduation_year || 2025,
          cgpa: pRes.data.cgpa || 8.0,
          phone: pRes.data.phone || '',
          location: pRes.data.location || '',
          daily_hours: pRes.data.daily_hours || 2.5,
          preferred_role: pRes.data.preferred_role || 'Software Developer',
          preferred_location: pRes.data.preferred_location || 'Bangalore',
          bio: pRes.data.bio || ''
        });
      }
      setSkills(sRes.data || []);
    } catch (e) {
      console.error(e);
      setError('Failed to load profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === 'graduation_year'
          ? parseInt(value)
          : name === 'cgpa' || name === 'daily_hours'
          ? parseFloat(value)
          : value
    }));
  };

  const handleSkillChange = (skillId, newLevel) => {
    setSkills((prev) =>
      prev.map((s) => (s.skill_id === skillId ? { ...s, level: parseInt(newLevel) } : s))
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');
    setError('');
    try {
      await api.put('/students/profile', formData);
      if (skills.length > 0) {
        await api.put('/students/skills', {
          skills: skills.map((s) => ({ skill_id: s.skill_id, level: s.level }))
        });
      }
      setSuccess('Profile and skills updated successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (e) {
      setError('Failed to update profile.');
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

  const levelOptions = [
    { value: 0, label: '0 - Not Started' },
    { value: 1, label: '1 - Beginner' },
    { value: 2, label: '2 - Basic' },
    { value: 3, label: '3 - Intermediate' },
    { value: 4, label: '4 - Advanced' },
    { value: 5, label: '5 - Expert' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Student Placement Profile
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Keep your academic parameters and verified skill proficiencies up-to-date
        </p>
      </div>

      {success && (
        <div className="flex items-center gap-2 rounded-2xl bg-emerald-50 p-4 text-xs font-semibold text-emerald-700 border border-emerald-200 shadow-xs">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 rounded-2xl bg-rose-50 p-4 text-xs font-semibold text-rose-700 border border-rose-200 shadow-xs">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Academic Profile Card */}
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-center gap-2.5 border-b border-slate-100 pb-4">
            <GraduationCap className="h-5 w-5 text-brand-600" />
            <h2 className="text-lg font-bold text-slate-900">Academic Credentials</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Full Name
              </label>
              <input
                type="text"
                required
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Email (Account Identifier)
              </label>
              <input
                type="email"
                disabled
                value={formData.email}
                className="w-full rounded-xl border border-slate-200 bg-slate-100 px-3.5 py-2.5 text-sm text-slate-500 cursor-not-allowed"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                College / University
              </label>
              <input
                type="text"
                name="college"
                value={formData.college}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Degree Program
              </label>
              <select
                name="degree"
                value={formData.degree}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              >
                <option value="B.Tech">B.Tech / B.E.</option>
                <option value="BCA">BCA / B.Sc (CS/IT)</option>
                <option value="MCA">MCA / M.Sc (CS/IT)</option>
                <option value="M.Tech">M.Tech</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Branch / Specialization
              </label>
              <input
                type="text"
                name="branch"
                value={formData.branch}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Graduation Year
              </label>
              <input
                type="number"
                name="graduation_year"
                value={formData.graduation_year}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Cumulative CGPA (out of 10)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="10"
                name="cgpa"
                value={formData.cgpa}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>
          </div>
        </div>

        {/* Preparation Preferences */}
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-center gap-2.5 border-b border-slate-100 pb-4">
            <Briefcase className="h-5 w-5 text-brand-600" />
            <h2 className="text-lg font-bold text-slate-900">Placement Target & Study Routine</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Preferred Job Role
              </label>
              <input
                type="text"
                name="preferred_role"
                value={formData.preferred_role}
                onChange={handleChange}
                placeholder="Software Developer"
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Preferred Work City
              </label>
              <input
                type="text"
                name="preferred_location"
                value={formData.preferred_location}
                onChange={handleChange}
                placeholder="Bangalore, Hyderabad"
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Daily Study Availability (Hours)
              </label>
              <input
                type="number"
                step="0.5"
                min="0.5"
                max="10"
                name="daily_hours"
                value={formData.daily_hours}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
            </div>
          </div>
        </div>

        {/* Technical & Core Skills Proficiency */}
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div className="flex items-center gap-2.5">
              <Award className="h-5 w-5 text-brand-600" />
              <div>
                <h2 className="text-lg font-bold text-slate-900">Current Skill Proficiencies</h2>
                <p className="text-xs text-slate-500">
                  Used directly by the Skill Gap Analysis and Roadmap Engine
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {skills.map((s) => (
              <div
                key={s.skill_id}
                className="rounded-2xl border border-slate-200/80 bg-slate-50/50 p-4 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold text-slate-900">{s.skill_name}</span>
                  <span className="text-[10px] font-semibold text-slate-400 uppercase">
                    {s.skill_category}
                  </span>
                </div>

                <select
                  value={s.level}
                  onChange={(e) => handleSkillChange(s.skill_id, e.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-xs font-medium text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                >
                  {levelOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 rounded-2xl bg-brand-600 px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-brand-500/25 hover:bg-brand-700 disabled:opacity-50 transition"
          >
            <Save className="h-4 w-4" />
            <span>{saving ? 'Saving Changes...' : 'Save Profile & Skill Matrix'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default Profile;
