import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import {
  Users,
  Building2,
  Database,
  GitBranch,
  CheckCircle2,
  Award,
  TrendingUp,
  ShieldCheck,
  Calendar
} from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [stRes, uRes] = await Promise.all([
        api.get('/admin/stats'),
        api.get('/admin/students')
      ]);
      setStats(stRes.data);
      setStudents(uRes.data || []);
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

  const statCards = [
    { label: 'Total Students', value: stats?.total_students || 0, icon: Users, color: 'text-indigo-600 bg-indigo-50' },
    { label: 'Total Companies', value: stats?.total_companies || 0, icon: Building2, color: 'text-blue-600 bg-blue-50' },
    { label: 'Question Bank', value: stats?.total_questions || 0, icon: Database, color: 'text-emerald-600 bg-emerald-50' },
    { label: 'Active Roadmaps', value: stats?.active_roadmaps || 0, icon: GitBranch, color: 'text-brand-600 bg-brand-50' },
    { label: 'Completed Tests', value: stats?.completed_tests || 0, icon: CheckCircle2, color: 'text-amber-600 bg-amber-50' },
    { label: 'Average Readiness', value: `${stats?.avg_readiness || 74}%`, icon: Award, color: 'text-purple-600 bg-purple-50' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-slate-900 text-white px-3 py-1 text-xs font-bold mb-2">
          <ShieldCheck className="h-3.5 w-3.5 text-brand-400" /> Platform Administration
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Admin Operations & Analytics Overview
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Monitor student enrollment, recruitment company templates, and scoring configuration
        </p>
      </div>

      {/* 6 Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {statCards.map((st, i) => {
          const Icon = st.icon;
          return (
            <div key={i} className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{st.label}</p>
                <p className="mt-2 text-3xl font-black text-slate-900">{st.value}</p>
              </div>
              <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${st.color}`}>
                <Icon className="h-6 w-6" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Registered Students Table */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">Enrolled Students</h2>
          <span className="text-xs text-slate-400">{students.length} Registered</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-3">Student Name</th>
                <th className="py-3 px-3">Email</th>
                <th className="py-3 px-3">College</th>
                <th className="py-3 px-3">CGPA</th>
                <th className="py-3 px-3">Target Role</th>
                <th className="py-3 px-3">Roadmaps</th>
                <th className="py-3 px-3">Tests</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 px-3 font-bold text-slate-900">{s.name}</td>
                  <td className="py-3.5 px-3 text-slate-500">{s.email}</td>
                  <td className="py-3.5 px-3 text-slate-600">{s.college || 'N/A'}</td>
                  <td className="py-3.5 px-3 font-bold text-brand-600">{s.cgpa || 'N/A'}</td>
                  <td className="py-3.5 px-3 text-slate-700">{s.preferred_role || 'Software Developer'}</td>
                  <td className="py-3.5 px-3">{s.roadmaps_count}</td>
                  <td className="py-3.5 px-3">{s.tests_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
