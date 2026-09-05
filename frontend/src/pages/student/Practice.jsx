import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../services/api';
import {
  HelpCircle,
  Clock,
  Sparkles,
  ArrowRight,
  Code,
  Database,
  BrainCircuit,
  BookOpen,
  CheckCircle2,
  Play
} from 'lucide-react';

const Practice = () => {
  const navigate = useNavigate();
  const [starting, setStarting] = useState(false);

  const categories = [
    { id: 'dsa', name: 'Data Structures & Algorithms', icon: Code, count: 15, desc: 'Arrays, Trees, Graphs, Sorting, Searching, DP' },
    { id: 'oop', name: 'Object-Oriented Programming', icon: BrainCircuit, count: 12, desc: 'Inheritance, Polymorphism, Encapsulation, SOLID' },
    { id: 'sql', name: 'SQL & Database Queries', icon: Database, count: 12, desc: 'JOINs, GROUP BY, Subqueries, Normalization' },
    { id: 'aptitude', name: 'Quantitative & Logical Aptitude', icon: BrainCircuit, count: 12, desc: 'Percentages, Time & Work, Speed & Distance, Puzzles' },
    { id: 'dbms', name: 'Database Management Systems', icon: Database, count: 10, desc: 'ACID, Concurrency, Normalization, Indexing' },
    { id: 'technical', name: 'Core Computer Science', icon: BookOpen, count: 12, desc: 'Operating Systems, Networks, Git, REST APIs' },
  ];

  const handleStartCategoryTest = async (catId) => {
    setStarting(true);
    try {
      const res = await api.post('/tests/start', {
        test_type: 'topic',
        category: catId,
        num_questions: 10,
        duration_minutes: 15
      });
      navigate(`/test/${res.data.test_id}`, { state: { testData: res.data } });
    } catch (e) {
      console.error(e);
    } finally {
      setStarting(false);
    }
  };

  const handleStartCompanyMock = async (companyName, qCount = 20, duration = 30) => {
    setStarting(true);
    try {
      const res = await api.post('/tests/start', {
        test_type: 'mock',
        num_questions: qCount,
        duration_minutes: duration
      });
      navigate(`/test/${res.data.test_id}`, { state: { testData: res.data } });
    } catch (e) {
      console.error(e);
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-bold text-brand-700 mb-2">
          <Sparkles className="h-3.5 w-3.5" /> Assessment Engine
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Practice Tests & Company Mock Assessments
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Take timed tests to benchmark your readiness. Scores automatically adapt your future preparation roadmap!
        </p>
      </div>

      {/* Full Mock Assessment Cards */}
      <div>
        <h2 className="text-base font-bold text-slate-900 mb-4">Company Comprehensive Mock Tests</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-3xl border border-brand-200 bg-gradient-to-br from-brand-50/50 to-indigo-50/30 p-6 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="rounded-md bg-brand-600 px-2 py-0.5 text-[10px] font-bold text-white uppercase tracking-wider">
                  TCS NQT Pattern
                </span>
                <span className="text-xs text-slate-500 font-medium">30 Mins</span>
              </div>
              <h3 className="font-extrabold text-slate-900 text-lg">TCS Technical & Aptitude Mock</h3>
              <p className="text-xs text-slate-500 mt-1">
                20 questions combining Aptitude, Verbal Ability, Core Java, and DSA fundamentals.
              </p>
            </div>
            <button
              onClick={() => handleStartCompanyMock('TCS', 20, 30)}
              disabled={starting}
              className="mt-6 flex items-center justify-center gap-2 rounded-2xl bg-brand-600 py-3 text-xs font-bold text-white shadow-md shadow-brand-500/25 hover:bg-brand-700 disabled:opacity-50 transition"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>Start TCS Mock Test</span>
            </button>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="rounded-md bg-slate-900 px-2 py-0.5 text-[10px] font-bold text-white uppercase tracking-wider">
                  Infosys SP / DSE
                </span>
                <span className="text-xs text-slate-500 font-medium">45 Mins</span>
              </div>
              <h3 className="font-extrabold text-slate-900 text-lg">Infosys Specialist Mock</h3>
              <p className="text-xs text-slate-500 mt-1">
                Advanced questions spanning OOP architecture, Data Structures, and relational query design.
              </p>
            </div>
            <button
              onClick={() => handleStartCompanyMock('Infosys', 25, 45)}
              disabled={starting}
              className="mt-6 flex items-center justify-center gap-2 rounded-2xl bg-slate-900 py-3 text-xs font-bold text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 transition"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>Start Infosys Mock Test</span>
            </button>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="rounded-md bg-rose-600 px-2 py-0.5 text-[10px] font-bold text-white uppercase tracking-wider">
                  Zoho Coding Screening
                </span>
                <span className="text-xs text-slate-500 font-medium">30 Mins</span>
              </div>
              <h3 className="font-extrabold text-slate-900 text-lg">Zoho Problem Solving Mock</h3>
              <p className="text-xs text-slate-500 mt-1">
                Heavy focus on loops, arrays, linked lists, complexity analysis, and OOP reasoning.
              </p>
            </div>
            <button
              onClick={() => handleStartCompanyMock('Zoho', 20, 30)}
              disabled={starting}
              className="mt-6 flex items-center justify-center gap-2 rounded-2xl bg-rose-600 py-3 text-xs font-bold text-white shadow-md shadow-rose-500/25 hover:bg-rose-700 disabled:opacity-50 transition"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>Start Zoho Mock Test</span>
            </button>
          </div>
        </div>
      </div>

      {/* Topic-Wise Practice Quizzes */}
      <div>
        <h2 className="text-base font-bold text-slate-900 mb-4">Topic-Wise Practice Quizzes (10 Questions)</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((c) => {
            const Icon = c.icon;
            return (
              <div
                key={c.id}
                className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-xs transition hover:shadow-md flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-100 text-brand-600">
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className="text-[11px] font-bold text-slate-400">{c.count}+ Questions</span>
                  </div>
                  <h3 className="font-extrabold text-slate-900 text-base">{c.name}</h3>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">{c.desc}</p>
                </div>

                <button
                  onClick={() => handleStartCategoryTest(c.id)}
                  disabled={starting}
                  className="mt-5 flex items-center justify-center gap-1.5 rounded-2xl border border-slate-200 bg-slate-50 py-2.5 text-xs font-bold text-slate-700 hover:bg-brand-50 hover:border-brand-200 hover:text-brand-700 transition"
                >
                  <span>Practice {c.name.split(' ')[0]}</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Practice;
