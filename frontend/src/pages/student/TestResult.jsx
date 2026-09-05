import React, { useState, useEffect } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import api from '../../services/api';
import {
  Award,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  ArrowRight,
  RefreshCw,
  GitBranch,
  AlertTriangle
} from 'lucide-react';

const TestResult = () => {
  const { id } = useParams();
  const location = useLocation();
  const [result, setResult] = useState(location.state?.resultData || null);
  const [review, setReview] = useState([]);
  const [loading, setLoading] = useState(!result);

  useEffect(() => {
    if (!result) {
      fetchResult();
    }
    fetchReview();
  }, [id]);

  const fetchResult = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/tests/${id}/results`);
      setReview(res.data.review || []);
      setResult({
        test_id: res.data.test_id,
        total_score: res.data.score,
        accuracy: res.data.accuracy,
        correct_count: res.data.correct_count,
        wrong_count: res.data.wrong_count,
        total_questions: (res.data.correct_count || 0) + (res.data.wrong_count || 0),
        time_taken_minutes: 15,
        topic_performance: [],
        weak_areas: [],
        roadmap_adapted: true
      });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchReview = async () => {
    try {
      const res = await api.get(`/tests/${id}/results`);
      setReview(res.data.review || []);
    } catch (e) {
      // ignore
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  const score = result?.total_score || 0;
  const isGood = score >= 75;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Result Hero Banner */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-8 shadow-xs text-center">
        <div
          className={`mx-auto flex h-20 w-20 items-center justify-center rounded-3xl text-3xl font-black shadow-lg ${
            isGood
              ? 'bg-emerald-100 text-emerald-700 shadow-emerald-500/20'
              : 'bg-amber-100 text-amber-700 shadow-amber-500/20'
          }`}
        >
          {score}%
        </div>

        <h1 className="mt-4 text-2xl font-black text-slate-900 tracking-tight">
          Assessment Completed
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-md mx-auto">
          {isGood
            ? 'Excellent demonstration of technical competence! Your roadmap has been automatically advanced.'
            : 'Good attempt. Targeted revision tasks have been incorporated into your active roadmap.'}
        </p>

        {/* Adaptive Alert Notice */}
        {result?.roadmap_adapted && (
          <div className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-indigo-50 px-4 py-2 text-xs font-semibold text-indigo-900 border border-indigo-100">
            <Sparkles className="h-4 w-4 text-brand-600 shrink-0" />
            <span>
              Roadmap adapted automatically based on your {score}% score!
            </span>
          </div>
        )}

        {/* Metrics Row */}
        <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-slate-100 pt-6">
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Accuracy</span>
            <p className="mt-1 text-xl font-extrabold text-slate-900">{result?.accuracy || score}%</p>
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Correct</span>
            <p className="mt-1 text-xl font-extrabold text-emerald-600">{result?.correct_count || 0}</p>
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Wrong</span>
            <p className="mt-1 text-xl font-extrabold text-rose-600">{result?.wrong_count || 0}</p>
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Time</span>
            <p className="mt-1 text-xl font-extrabold text-slate-900">
              {result?.time_taken_minutes || 15} min
            </p>
          </div>
        </div>
      </div>

      {/* Topic-Wise Breakdown & Weak Areas */}
      {result?.topic_performance?.length > 0 && (
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
          <h2 className="text-base font-bold text-slate-900 mb-4">Topic-Wise Performance</h2>
          <div className="space-y-3">
            {result.topic_performance.map((tp) => (
              <div key={tp.topic} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-700">
                  <span>{tp.topic}</span>
                  <span>
                    {tp.correct}/{tp.total} ({tp.score}%)
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${tp.score}%`,
                      backgroundColor: tp.score >= 70 ? '#10b981' : tp.score >= 50 ? '#f59e0b' : '#ef4444'
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Answer Review & Detailed Explanations */}
      {review.length > 0 && (
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-base font-bold text-slate-900">Detailed Answer Explanations</h2>
            <span className="text-xs text-slate-400">{review.length} Questions Reviewed</span>
          </div>

          <div className="space-y-4">
            {review.map((item, idx) => (
              <div
                key={item.question_id || idx}
                className={`rounded-2xl border p-5 transition ${
                  item.is_correct ? 'border-emerald-200 bg-emerald-50/20' : 'border-rose-200 bg-rose-50/20'
                }`}
              >
                <div className="flex items-start justify-between gap-3 mb-2">
                  <span className="text-xs font-bold text-slate-500">Q{idx + 1} &bull; {item.topic}</span>
                  {item.is_correct ? (
                    <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600">
                      <CheckCircle2 className="h-4 w-4" /> Correct
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs font-bold text-rose-600">
                      <XCircle className="h-4 w-4" /> Incorrect
                    </span>
                  )}
                </div>

                <p className="text-sm font-bold text-slate-900">{item.question_text}</p>

                <div className="mt-3 text-xs space-y-1">
                  <p className="text-slate-600">
                    <span className="font-semibold text-slate-700">Your Answer: </span>
                    <span className={item.is_correct ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}>
                      {item.selected_option_text}
                    </span>
                  </p>
                  {!item.is_correct && (
                    <p className="text-emerald-700">
                      <span className="font-semibold">Correct Answer: </span>
                      <span className="font-bold">{item.correct_option_text}</span>
                    </p>
                  )}
                </div>

                {item.explanation && (
                  <div className="mt-3 rounded-xl bg-white p-3 text-xs text-slate-600 border border-slate-100 shadow-2xs">
                    <span className="font-bold text-slate-800">Explanation: </span>
                    {item.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Footer */}
      <div className="flex items-center justify-between">
        <Link
          to="/practice"
          className="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-xs font-bold text-slate-700 hover:bg-slate-50 transition shadow-xs"
        >
          Practice More Tests
        </Link>
        <Link
          to="/roadmap"
          className="flex items-center gap-1.5 rounded-2xl bg-brand-600 px-6 py-3 text-xs font-bold text-white shadow-md shadow-brand-500/25 hover:bg-brand-700 transition"
        >
          <span>Return to Roadmap</span>
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
};

export default TestResult;
