import React, { useState, useEffect, useRef } from 'react';
import api from '../../services/api';
import {
  MessageSquare,
  Send,
  Sparkles,
  Bot,
  User,
  Award,
  CheckCircle2,
  AlertCircle,
  Clock,
  RotateCcw,
  Lightbulb
} from 'lucide-react';

const MockInterview = () => {
  const [interviewId, setInterviewId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [starting, setStarting] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewInterview = async () => {
    setStarting(true);
    setEvaluation(null);
    setIsCompleted(false);
    try {
      const res = await api.post('/interviews/start', {
        interview_type: 'technical'
      });
      setInterviewId(res.data.interview_id);
      setMessages([{ role: 'ai', content: res.data.ai_message }]);
    } catch (e) {
      console.error(e);
    } finally {
      setStarting(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || !interviewId || isCompleted) return;

    const studentText = input;
    setInput('');
    setMessages((prev) => [...prev, { role: 'student', content: studentText }]);
    setLoading(true);

    try {
      const res = await api.post(`/interviews/${interviewId}/message`, {
        content: studentText
      });
      setMessages((prev) => [...prev, { role: 'ai', content: res.data.ai_message }]);
      if (res.data.is_completed) {
        setIsCompleted(true);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleEndInterview = async () => {
    if (!interviewId) return;
    setLoading(true);
    try {
      const res = await api.post(`/interviews/${interviewId}/end`);
      setEvaluation(res.data);
      setIsCompleted(true);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-bold text-brand-700 mb-2">
            <Sparkles className="h-3.5 w-3.5" /> AI Technical Interviewer
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Interactive Placement Mock Interview
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Simulate real technical and HR interview rounds with dynamic follow-up questions
          </p>
        </div>

        {!interviewId ? (
          <button
            onClick={startNewInterview}
            disabled={starting}
            className="flex items-center gap-2 rounded-2xl bg-brand-600 px-5 py-3 text-xs font-bold text-white shadow-lg shadow-brand-500/25 hover:bg-brand-700 disabled:opacity-50 transition"
          >
            <Sparkles className="h-4 w-4" />
            <span>{starting ? 'Initializing Session...' : 'Start Mock Interview'}</span>
          </button>
        ) : (
          <div className="flex items-center gap-2">
            {!isCompleted && (
              <button
                onClick={handleEndInterview}
                disabled={loading}
                className="rounded-2xl border border-slate-300 bg-white px-4 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50 shadow-xs transition"
              >
                End & Get Evaluation
              </button>
            )}
            <button
              onClick={startNewInterview}
              className="rounded-2xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white hover:bg-slate-800 shadow-xs transition"
            >
              Restart
            </button>
          </div>
        )}
      </div>

      {!interviewId && (
        <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-xs">
          <Bot className="mx-auto h-16 w-16 text-brand-600 mb-4" />
          <h2 className="text-xl font-black text-slate-900">Ready to Practice Your Interview?</h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-500 max-w-md mx-auto leading-relaxed">
            The AI interviewer evaluates your technical depth, communication clarity, project defense,
            and situational awareness. At the end, you will receive a comprehensive scorecard.
          </p>
          <button
            onClick={startNewInterview}
            disabled={starting}
            className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-brand-600 px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-brand-500/25 hover:bg-brand-700 transition"
          >
            <Sparkles className="h-4 w-4" />
            <span>Begin Technical Interview</span>
          </button>
        </div>
      )}

      {/* Evaluation Results Card */}
      {evaluation && (
        <div className="rounded-3xl border border-brand-200 bg-gradient-to-br from-brand-50/50 to-indigo-50/30 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-brand-100 pb-4">
            <div className="flex items-center gap-2.5">
              <Award className="h-6 w-6 text-brand-600" />
              <h2 className="text-lg font-black text-slate-900">Performance Evaluation Summary</h2>
            </div>
            <span className="text-2xl font-black text-brand-600">
              {evaluation.overall_score || 75}% Overall
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-2xl bg-white p-4 border border-brand-100/80 shadow-xs">
              <span className="text-[11px] font-bold text-slate-400 uppercase">Technical Knowledge</span>
              <p className="mt-1 text-2xl font-black text-slate-900">{evaluation.tech_score || 75}%</p>
            </div>
            <div className="rounded-2xl bg-white p-4 border border-brand-100/80 shadow-xs">
              <span className="text-[11px] font-bold text-slate-400 uppercase">Communication Clarity</span>
              <p className="mt-1 text-2xl font-black text-slate-900">{evaluation.comm_score || 75}%</p>
            </div>
            <div className="rounded-2xl bg-white p-4 border border-brand-100/80 shadow-xs">
              <span className="text-[11px] font-bold text-slate-400 uppercase">Answer Relevance</span>
              <p className="mt-1 text-2xl font-black text-slate-900">{evaluation.relevance_score || 75}%</p>
            </div>
          </div>

          {evaluation.feedback && (
            <div className="rounded-2xl bg-white p-5 border border-brand-100/80 shadow-xs">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5 flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" /> Interviwer Feedback
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">{evaluation.feedback}</p>
            </div>
          )}

          {evaluation.suggestions && (
            <div className="rounded-2xl bg-white p-5 border border-brand-100/80 shadow-xs">
              <h3 className="text-xs font-bold uppercase tracking-wider text-amber-700 mb-1.5 flex items-center gap-1.5">
                <Lightbulb className="h-4 w-4 text-amber-500" /> Actionable Improvement Points
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-line">
                {evaluation.suggestions}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Chat Messages Log */}
      {interviewId && (
        <div className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-xs flex flex-col h-[520px]">
          <div className="flex-1 overflow-y-auto space-y-4 pr-2">
            {messages.map((m, idx) => {
              const isAi = m.role === 'ai';
              return (
                <div
                  key={idx}
                  className={`flex items-start gap-3 ${isAi ? 'justify-start' : 'justify-end'}`}
                >
                  {isAi && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white font-bold text-xs shadow-xs">
                      AI
                    </div>
                  )}

                  <div
                    className={`rounded-2xl p-4 max-w-[82%] text-xs sm:text-sm leading-relaxed ${
                      isAi
                        ? 'bg-slate-100 text-slate-800'
                        : 'bg-brand-600 text-white shadow-xs shadow-brand-500/10'
                    }`}
                  >
                    {m.content}
                  </div>

                  {!isAi && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white font-bold text-xs">
                      You
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex items-center gap-2 text-xs text-slate-400 py-2">
                <div className="h-2 w-2 animate-bounce rounded-full bg-brand-500" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-brand-500 [animation-delay:0.2s]" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-brand-500 [animation-delay:0.4s]" />
                <span>Interviewer is evaluating your response...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          {!isCompleted ? (
            <form onSubmit={handleSendMessage} className="mt-4 pt-3 border-t border-slate-100 flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
                placeholder="Type your structured answer here (press Enter to send)..."
                className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-md shadow-brand-500/25 hover:bg-brand-700 disabled:opacity-40 transition shrink-0"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          ) : (
            <div className="mt-4 pt-3 border-t border-slate-100 text-center text-xs text-slate-400">
              Interview session concluded. Review the detailed scorecard above.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MockInterview;
