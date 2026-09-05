import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  User,
  Building2,
  GitBranch,
  CalendarCheck,
  CheckSquare,
  HelpCircle,
  MessageSquare,
  FileText,
  FolderGit2,
  BarChart3,
  Scale,
  Settings,
  Database,
  Sliders
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
  const { isAdmin } = useAuth();

  const studentLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/companies', label: 'Companies', icon: Building2 },
    { to: '/roadmap', label: 'My Roadmap', icon: GitBranch },
    { to: '/tasks', label: "Today's Tasks", icon: CalendarCheck },
    { to: '/skill-gap', label: 'Skill Gap & Readiness', icon: CheckSquare },
    { to: '/practice', label: 'Practice & Mock Tests', icon: HelpCircle },
    { to: '/mock-interview', label: 'AI Mock Interview', icon: MessageSquare },
    { to: '/resume', label: 'Resume Analysis', icon: FileText },
    { to: '/projects', label: 'Recommended Projects', icon: FolderGit2 },
    { to: '/compare', label: 'Compare Companies', icon: Scale },
    { to: '/progress', label: 'Progress Analytics', icon: BarChart3 },
    { to: '/profile', label: 'My Profile & Skills', icon: User },
  ];

  const adminLinks = [
    { to: '/admin', label: 'Overview & Stats', icon: LayoutDashboard },
    { to: '/admin/companies', label: 'Manage Companies', icon: Building2 },
    { to: '/admin/questions', label: 'Question Bank', icon: Database },
    { to: '/admin/weights', label: 'Readiness Weights', icon: Sliders },
  ];

  const links = isAdmin ? adminLinks : studentLinks;

  return (
    <aside className="sticky top-16 h-[calc(100vh-4rem)] w-64 shrink-0 border-r border-slate-200 bg-white p-4 hidden md:flex flex-col justify-between overflow-y-auto">
      <div className="space-y-1">
        <div className="px-3 py-2">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            {isAdmin ? 'Administration' : 'Placement Planner'}
          </p>
        </div>
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-sm shadow-brand-500/30'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span>{link.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="rounded-2xl border border-slate-100 bg-slate-50/80 p-3 text-xs text-slate-500">
        <p className="font-semibold text-slate-700">Targeting Placements?</p>
        <p className="mt-0.5 text-[11px] text-slate-500">
          Complete daily tasks to raise your Company Readiness score!
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
