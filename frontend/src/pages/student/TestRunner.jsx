import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { Clock, AlertTriangle, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';

const TestRunner = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [testData, setTestData] = useState(location.state?.testData || null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({}); // question_id -> option_id
  const [timeLeft, setTimeLeft] = useState(30 * 60); // seconds
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!testData) {
      // If refreshed or accessed directly, redirect to practice
      navigate('/practice');
      return;
    }
    setTimeLeft(testData.duration_minutes * 60);
  }, [testData]);

  useEffect(() => {
    if (timeLeft <= 0) {
      handleSubmit();
      return;
    }
    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleSelectOption = (questionId, optionId) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionId
    }));
  };

  const handleSubmit = async () => {
    if (submitting) return;
    setSubmitting(true);
    try {
      const payload = {
        answers: testData.questions.map((q) => ({
          question_id: q.id,
          selected_option_id: answers[q.id] || null,
          time_taken_seconds: 30
        }))
      };
      const res = await api.post(`/tests/${id}/submit`, payload);
      navigate(`/test/${id}/result`, { state: { resultData: res.data } });
    } catch (e) {
      console.error(e);
      alert('Error submitting test. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!testData) return null;

  const currentQ = testData.questions[currentIdx];
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header with Timer */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs flex items-center justify-between">
        <div>
          <span className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-bold text-brand-600">
            Active Assessment
          </span>
          <h1 className="mt-1 text-base font-bold text-slate-900">
            Question {currentIdx + 1} of {testData.questions.length}
          </h1>
        </div>

        {/* Live Timer Pill */}
        <div
          className={`flex items-center gap-2 rounded-2xl px-4 py-2 text-sm font-black border transition ${
            timeLeft < 300
              ? 'bg-rose-50 text-rose-600 border-rose-200 animate-pulse'
              : 'bg-slate-100 text-slate-800 border-slate-200'
          }`}
        >
          <Clock className="h-4 w-4" />
          <span>
            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
          </span>
        </div>
      </div>

      {/* Main Question Card */}
      <div className="rounded-3xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-100 pb-3">
          <span className="font-bold text-brand-600 uppercase tracking-wider">{currentQ.category}</span>
          <span className="capitalize bg-slate-100 px-2 py-0.5 rounded text-slate-600 font-medium">
            {currentQ.difficulty}
          </span>
        </div>

        <p className="text-base sm:text-lg font-bold text-slate-900 leading-relaxed">
          {currentQ.question_text}
        </p>

        {/* Options */}
        <div className="space-y-3 pt-2">
          {currentQ.options?.map((opt, idx) => {
            const isSelected = answers[currentQ.id] === opt.id;
            const letters = ['A', 'B', 'C', 'D'];
            return (
              <div
                key={opt.id}
                onClick={() => handleSelectOption(currentQ.id, opt.id)}
                className={`cursor-pointer rounded-2xl border p-4 transition flex items-center gap-3.5 ${
                  isSelected
                    ? 'border-brand-500 bg-brand-50/50 text-slate-900 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                }`}
              >
                <div
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-xl font-bold text-xs transition ${
                    isSelected ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {letters[idx] || idx + 1}
                </div>
                <span className="text-sm font-medium">{opt.option_text}</span>
              </div>
            );
          })}
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-100">
          <button
            type="button"
            onClick={() => setCurrentIdx((prev) => Math.max(0, prev - 1))}
            disabled={currentIdx === 0}
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-40 transition"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Previous</span>
          </button>

          {currentIdx < testData.questions.length - 1 ? (
            <button
              type="button"
              onClick={() => setCurrentIdx((prev) => prev + 1)}
              className="flex items-center gap-1.5 rounded-xl bg-slate-900 px-5 py-2.5 text-xs font-bold text-white hover:bg-slate-800 transition shadow-xs"
            >
              <span>Next</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center gap-1.5 rounded-xl bg-emerald-600 px-6 py-2.5 text-xs font-bold text-white hover:bg-emerald-700 shadow-md shadow-emerald-600/20 disabled:opacity-50 transition"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>{submitting ? 'Submitting...' : 'Submit Test'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Question Quick Palette */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
        <div className="flex items-center justify-between mb-3 text-xs">
          <span className="font-bold text-slate-700">Question Navigation Palette</span>
          <span className="text-slate-400">
            {answeredCount} of {testData.questions.length} answered
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {testData.questions.map((q, idx) => {
            const isAnswered = !!answers[q.id];
            const isCurrent = currentIdx === idx;
            return (
              <button
                key={q.id}
                onClick={() => setCurrentIdx(idx)}
                className={`h-8 w-8 rounded-xl font-bold text-xs transition ${
                  isCurrent
                    ? 'ring-2 ring-brand-500 ring-offset-1 bg-brand-600 text-white'
                    : isAnswered
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TestRunner;
