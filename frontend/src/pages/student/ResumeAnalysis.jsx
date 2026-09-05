import React, { useState } from 'react';
import api from '../../services/api';
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Briefcase,
  Layers,
  Lightbulb
} from 'lucide-react';

const ResumeAnalysis = () => {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a PDF or TXT resume file first.');
      return;
    }
    setAnalyzing(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      // Optional company_role_id
      formData.append('company_role_id', '1');

      const res = await api.post('/resume/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to extract text from resume. Please ensure it is a text PDF.'
      );
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-bold text-brand-700 mb-2">
          <Sparkles className="h-3.5 w-3.5" /> Resume Match Engine
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Resume Skill Analysis & Gap Identification
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Upload your resume to extract skills and compare directly against recruiter role benchmarks
        </p>
      </div>

      {/* Upload Box */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-8 shadow-xs">
        <form onSubmit={handleUpload} className="space-y-6">
          <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 p-8 text-center transition hover:border-brand-400 bg-slate-50/50">
            <UploadCloud className="h-12 w-12 text-brand-600 mb-3" />
            <h3 className="text-sm font-bold text-slate-900">
              {file ? file.name : 'Upload your resume (PDF or TXT)'}
            </h3>
            <p className="mt-1 text-xs text-slate-500 max-w-sm">
              Text-based PDFs or raw text resumes are supported for automatic NLP extraction
            </p>

            <label className="mt-4 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white transition hover:bg-brand-600 shadow-xs">
              <span>Choose Resume File</span>
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>

          {error && (
            <div className="flex items-center gap-2 rounded-xl bg-rose-50 p-3 text-xs font-semibold text-rose-700 border border-rose-200">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={analyzing || !file}
              className="flex items-center gap-2 rounded-2xl bg-brand-600 px-6 py-3 text-xs font-bold text-white shadow-md shadow-brand-500/25 hover:bg-brand-700 disabled:opacity-50 transition"
            >
              {analyzing ? 'Extracting & Comparing Skills...' : 'Analyze Resume'}
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </form>
      </div>

      {/* Analysis Results */}
      {result && (
        <div className="space-y-6">
          {/* Match Score Card */}
          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-6">
            <div>
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700 border border-brand-200">
                Company Target Match
              </span>
              <h2 className="mt-3 text-2xl font-black text-slate-900">
                {result.match_score}% Skills Alignment
              </h2>
              <p className="mt-1 text-xs text-slate-500 max-w-md">
                Comparing skills found in your document with standard recruitment role requirements.
              </p>
            </div>

            <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-3xl bg-brand-50 border-2 border-brand-500 font-black text-2xl text-brand-600 shadow-sm">
              {result.match_score}%
            </div>
          </div>

          {/* Matched vs Missing Skills Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Matched */}
            <div className="rounded-3xl border border-emerald-200 bg-emerald-50/30 p-6 shadow-xs">
              <h3 className="text-sm font-extrabold text-emerald-900 flex items-center gap-2 mb-4">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                Matched Skills in Resume ({result.matched_skills?.length || 0})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.matched_skills?.map((s, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-xl bg-white border border-emerald-200 px-3 py-1 text-xs font-bold text-emerald-700 shadow-2xs"
                  >
                    ✓ {s}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing */}
            <div className="rounded-3xl border border-rose-200 bg-rose-50/30 p-6 shadow-xs">
              <h3 className="text-sm font-extrabold text-rose-900 flex items-center gap-2 mb-4">
                <XCircle className="h-4 w-4 text-rose-600" />
                Missing or Weak Skills ({result.missing_skills?.length || 0})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.missing_skills?.map((s, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-xl bg-white border border-rose-200 px-3 py-1 text-xs font-bold text-rose-700 shadow-2xs"
                  >
                    ✗ {s}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Recommendations Callout */}
          {result.recommendations?.length > 0 && (
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-1.5">
                <Lightbulb className="h-4 w-4 text-amber-500" /> Strategic Profile Recommendations
              </h3>
              <ul className="space-y-2 text-xs text-slate-600">
                {result.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-brand-600 font-bold">&bull;</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResumeAnalysis;
