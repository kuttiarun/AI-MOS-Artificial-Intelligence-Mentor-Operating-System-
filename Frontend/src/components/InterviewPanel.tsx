/**
 * AI-MOS — Interview Mode Panel
 * ==============================
 * Full-screen interview simulation powered by Srinivasan (15+ YOE Zoho Panelist).
 * Connects to:
 *   POST /api/v1/interview/start  — initializes session
 *   POST /api/v1/interview/chat   — submits answer, returns score + next question
 *
 * Features:
 *   - Score badge (0-10) with red/amber/green color coding
 *   - Conversation thread with interviewer/candidate bubbles
 *   - Topic selector for targeted topic practice
 *   - Session stats: questions asked, avg score, pass rate
 */

import React, { useState, useRef, useEffect } from "react";
import {
  Target,
  Send,
  Mic,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ChevronDown,
  RefreshCw,
  TrendingUp,
  Award,
  Zap,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface ChatMessage {
  role: "interviewer" | "candidate";
  content: string;
  score?: number;
  isLoading?: boolean;
}

interface InterviewStats {
  questionsAsked: number;
  totalScore: number;
  passes: number;
}

const INTERVIEW_TOPICS = [
  { id: "java-core-oop-classes",        label: "OOP & Classes" },
  { id: "java-collections-hashmap",     label: "HashMap Internals" },
  { id: "java-advanced-concurrency",    label: "Concurrency & Threads" },
  { id: "java-advanced-jvm-memory",     label: "JVM Memory Model" },
  { id: "java-advanced-streams",        label: "Streams & Lambdas" },
  { id: "spring-data-jpa",             label: "Spring Data JPA" },
  { id: "spring-security",             label: "Spring Security & JWT" },
  { id: "testing-mockito",             label: "Mockito & Testing" },
  { id: "spring-rest-design",          label: "REST API Design" },
];

// ─── Score Badge ─────────────────────────────────────────────────────────────

const ScoreBadge: React.FC<{ score: number }> = ({ score }) => {
  const color =
    score >= 8 ? "text-emerald-400 border-emerald-700 bg-emerald-950/40"
    : score >= 6 ? "text-amber-400 border-amber-700 bg-amber-950/40"
    : "text-red-400 border-red-800 bg-red-950/30";
  const label = score >= 8 ? "Excellent" : score >= 6 ? "Acceptable" : "Needs Work";

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-bold ${color}`}
    >
      {score}/10 · {label}
    </span>
  );
};

// ─── Main Component ───────────────────────────────────────────────────────────

interface InterviewPanelProps {
  onGoBack: () => void;
}

export const InterviewPanel: React.FC<InterviewPanelProps> = ({ onGoBack }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState(INTERVIEW_TOPICS[0].id);
  const [isTopicOpen, setIsTopicOpen] = useState(false);
  const [stats, setStats] = useState<InterviewStats>({ questionsAsked: 0, totalScore: 0, passes: 0 });
  const [error, setError] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const getApiHeaders = () => {
    const apiKey = localStorage.getItem("aimos_api_key") || "";
    const provider = localStorage.getItem("aimos_provider") || "nvidia-nim";
    const userId = localStorage.getItem("aimos_user_id") || "";
    return {
      "Content-Type": "application/json",
      "X-User-API-Key": apiKey,
      "X-User-Provider": provider,
      ...(userId ? { "X-User-Id": userId } : {}),
    };
  };

  const startSession = async () => {
    setError(null);
    setIsLoading(true);
    setMessages([]);
    setStats({ questionsAsked: 0, totalScore: 0, passes: 0 });

    try {
      const resp = await fetch("http://localhost:8000/api/v1/interview/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!resp.ok) throw new Error("Failed to start interview session.");
      const data = await resp.json();
      setMessages([{ role: "interviewer", content: data.initial_question }]);
      setSessionStarted(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error starting session.");
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!inputText.trim() || isLoading) return;

    const candidateText = inputText.trim();
    setInputText("");

    const candidateMsg: ChatMessage = { role: "candidate", content: candidateText };
    const loadingMsg: ChatMessage = { role: "interviewer", content: "Evaluating your response…", isLoading: true };

    setMessages(prev => [...prev, candidateMsg, loadingMsg]);
    setIsLoading(true);
    setError(null);

    const history = messages.map(m => ({
      role: m.role === "interviewer" ? "assistant" : "user",
      content: m.content,
    }));

    try {
      const resp = await fetch("http://localhost:8000/api/v1/interview/chat", {
        method: "POST",
        headers: getApiHeaders(),
        body: JSON.stringify({
          node_id: selectedTopic,
          candidate_answer: candidateText,
          chat_history: history,
        }),
      });

      if (!resp.ok) throw new Error(`Interview API error: ${resp.status}`);
      const data = await resp.json();

      const responseText = `${data.critique}\n\n**Next question:** ${data.next_question}`;

      setMessages(prev => [
        ...prev.slice(0, -1), // remove loading bubble
        { role: "interviewer", content: responseText, score: data.score },
      ]);

      setStats(prev => ({
        questionsAsked: prev.questionsAsked + 1,
        totalScore: prev.totalScore + data.score,
        passes: prev.passes + (data.passed ? 1 : 0),
      }));
    } catch (e: unknown) {
      setMessages(prev => prev.slice(0, -1));
      setError(e instanceof Error ? e.message : "Evaluation failed. Check your API key.");
    } finally {
      setIsLoading(false);
    }
  };

  const avgScore = stats.questionsAsked > 0 ? Math.round(stats.totalScore / stats.questionsAsked) : 0;
  const passRate = stats.questionsAsked > 0 ? Math.round((stats.passes / stats.questionsAsked) * 100) : 0;
  const selectedLabel = INTERVIEW_TOPICS.find(t => t.id === selectedTopic)?.label ?? "Unknown";

  return (
    <div className="flex h-full flex-col bg-slate-950 text-slate-100 overflow-hidden">
      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <div className="border-b border-slate-800 bg-slate-900/70 px-5 py-3 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Recording dot */}
            <div className="relative">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-red-600 to-rose-700 flex items-center justify-center shadow-lg shadow-red-950/60">
                <Mic size={14} className="text-white" />
              </div>
              <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-red-500 border-2 border-slate-900 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold text-slate-100">Srinivasan · Zoho Technical Panel</h1>
                <span className="rounded-full bg-red-950/50 px-2 py-0.5 text-[9px] font-bold text-red-400 border border-red-900/50 uppercase tracking-widest">
                  Live Simulation
                </span>
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">
                Senior Architect · 15+ YOE · Zoho Java Compiler Core Team
              </p>
            </div>
          </div>

          <button
            onClick={onGoBack}
            className="rounded-lg border border-slate-800 px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-all"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>

      {/* ── Session Stats ────────────────────────────────────────────────────── */}
      {sessionStarted && (
        <div className="flex gap-3 px-5 py-2.5 border-b border-slate-800/60 bg-slate-900/30 shrink-0">
          <div className="flex items-center gap-1.5 text-xs">
            <Zap size={11} className="text-amber-400" />
            <span className="text-slate-400">Questions:</span>
            <span className="font-bold text-slate-200">{stats.questionsAsked}</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <TrendingUp size={11} className="text-indigo-400" />
            <span className="text-slate-400">Avg Score:</span>
            <span className={`font-bold ${avgScore >= 7 ? "text-emerald-400" : avgScore >= 5 ? "text-amber-400" : "text-red-400"}`}>
              {stats.questionsAsked > 0 ? avgScore : "—"}/10
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <Award size={11} className="text-emerald-400" />
            <span className="text-slate-400">Pass Rate:</span>
            <span className={`font-bold ${passRate >= 60 ? "text-emerald-400" : "text-red-400"}`}>
              {stats.questionsAsked > 0 ? `${passRate}%` : "—"}
            </span>
          </div>
          <div className="ml-auto flex items-center gap-1.5 text-xs">
            <span className="text-slate-500">Topic:</span>
            <span className="font-semibold text-indigo-300">{selectedLabel}</span>
          </div>
        </div>
      )}

      {/* ── Pre-session Setup or Chat Thread ─────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto">
        {!sessionStarted ? (
          /* ── Welcome / Setup Screen ─── */
          <div className="flex h-full flex-col items-center justify-center px-8 text-center gap-6">
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-red-700 to-rose-600 flex items-center justify-center shadow-2xl shadow-red-950/80">
              <Target size={28} className="text-white" />
            </div>

            <div>
              <h2 className="text-xl font-bold text-slate-100">Zoho Mock Interview Simulator</h2>
              <p className="mt-2 text-sm text-slate-400 max-w-md leading-relaxed">
                You will be interviewed by <span className="text-red-400 font-semibold">Srinivasan</span>, a
                Senior Architect with 15+ years at Zoho. Answers are scored 0–10 using the STAR-T rubric.
                A score of 6+ is a pass.
              </p>
            </div>

            {/* Topic Selector */}
            <div className="w-full max-w-sm">
              <label className="block text-xs font-semibold text-slate-400 mb-2 text-left">
                Select Interview Topic
              </label>
              <div className="relative">
                <button
                  onClick={() => setIsTopicOpen(o => !o)}
                  className="flex w-full items-center justify-between rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 hover:border-slate-600 transition-all"
                >
                  <span>{selectedLabel}</span>
                  <ChevronDown size={14} className={`text-slate-400 transition-transform ${isTopicOpen ? "rotate-180" : ""}`} />
                </button>
                {isTopicOpen && (
                  <div className="absolute top-full left-0 right-0 mt-1 rounded-xl border border-slate-700 bg-slate-900 shadow-2xl z-50 overflow-hidden">
                    {INTERVIEW_TOPICS.map(t => (
                      <button
                        key={t.id}
                        onClick={() => { setSelectedTopic(t.id); setIsTopicOpen(false); }}
                        className={`flex w-full items-center px-4 py-2.5 text-sm text-left transition-colors ${
                          selectedTopic === t.id ? "bg-red-950/40 text-red-300" : "text-slate-300 hover:bg-slate-800"
                        }`}
                      >
                        {t.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-lg border border-red-900/50 bg-red-950/20 px-4 py-3 text-sm text-red-400 w-full max-w-sm">
                <AlertTriangle size={14} />
                <span>{error}</span>
              </div>
            )}

            <button
              onClick={startSession}
              disabled={isLoading}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-red-700 to-rose-600 px-8 py-3 text-sm font-bold text-white shadow-lg shadow-red-950/60 hover:from-red-600 hover:to-rose-500 transition-all disabled:opacity-60"
            >
              {isLoading ? <RefreshCw size={14} className="animate-spin" /> : <Mic size={14} />}
              {isLoading ? "Connecting to Panel…" : "Begin Interview Session"}
            </button>

            <p className="text-[10px] text-slate-600">
              Requires API key configured in settings · Scores logged to your weak areas tracker
            </p>
          </div>
        ) : (
          /* ── Chat Thread ─── */
          <div className="p-5 space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "candidate" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === "candidate"
                      ? "bg-indigo-700/30 border border-indigo-700/50 text-indigo-100 rounded-tr-sm"
                      : msg.isLoading
                        ? "bg-slate-900 border border-slate-800 text-slate-500 rounded-tl-sm animate-pulse"
                        : "bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-sm"
                  }`}
                >
                  {msg.role === "interviewer" && !msg.isLoading && (
                    <div className="flex items-center gap-1.5 mb-2">
                      <div className="h-4 w-4 rounded-full bg-gradient-to-br from-red-600 to-rose-700 flex items-center justify-center">
                        <Mic size={8} className="text-white" />
                      </div>
                      <span className="text-[10px] font-bold text-red-400">SRINIVASAN</span>
                      {msg.score !== undefined && <ScoreBadge score={msg.score} />}
                    </div>
                  )}
                  {msg.role === "candidate" && (
                    <div className="flex items-center justify-end gap-1.5 mb-2">
                      <span className="text-[10px] font-bold text-indigo-400">YOU</span>
                    </div>
                  )}
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  {/* Score visualization */}
                  {msg.score !== undefined && (
                    <div className="mt-3 flex items-center gap-2">
                      <div className="flex-1 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-700 ${
                            msg.score >= 8 ? "bg-emerald-500" : msg.score >= 6 ? "bg-amber-500" : "bg-red-500"
                          }`}
                          style={{ width: `${(msg.score / 10) * 100}%` }}
                        />
                      </div>
                      {msg.score >= 6
                        ? <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                        : <XCircle size={13} className="text-red-400 shrink-0" />
                      }
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      {/* ── Input Bar (only shown when session active) ───────────────────────── */}
      {sessionStarted && (
        <div className="border-t border-slate-800 bg-slate-900/60 p-4 shrink-0">
          {error && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-red-900/40 bg-red-950/20 px-3 py-2 text-xs text-red-400">
              <AlertTriangle size={12} />
              <span>{error}</span>
            </div>
          )}
          <div className="flex gap-2">
            <textarea
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submitAnswer(); }
              }}
              placeholder="Type your answer… (Enter to submit, Shift+Enter for new line)"
              rows={3}
              disabled={isLoading}
              className="flex-1 resize-none rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-600 focus:border-red-700/60 focus:outline-none focus:ring-1 focus:ring-red-800/40 disabled:opacity-60 transition-all"
            />
            <div className="flex flex-col gap-2">
              <button
                onClick={submitAnswer}
                disabled={isLoading || !inputText.trim()}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-red-700 to-rose-600 text-white shadow-lg hover:from-red-600 hover:to-rose-500 transition-all disabled:opacity-40"
              >
                {isLoading ? <RefreshCw size={14} className="animate-spin" /> : <Send size={14} />}
              </button>
              <button
                onClick={() => { setSessionStarted(false); setMessages([]); }}
                title="Restart session"
                className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-700 text-slate-500 hover:text-slate-300 hover:border-slate-600 transition-all"
              >
                <RefreshCw size={14} />
              </button>
            </div>
          </div>
          <p className="mt-2 text-[10px] text-slate-600 text-center">
            Your answers are scored using the STAR-T rubric (Situation, Task, Action, Result, Trade-offs)
          </p>
        </div>
      )}
    </div>
  );
};
