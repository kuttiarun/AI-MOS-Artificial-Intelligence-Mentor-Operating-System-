/**
 * AI-MOS DashboardOverview
 * ========================
 * The Operating System home screen. Shown when no lesson is selected.
 * Provides a mission-control-style overview of:
 *   - Student target role & baseline profile
 *   - Overall syllabus completion percentage
 *   - Phase-by-phase progress breakdown
 *   - Active weak areas (from curriculum progress data)
 *   - "Continue Learning" CTA that routes to the active node
 */

import React, { useEffect, useState, useMemo } from "react";
import {
  LayoutDashboard,
  Target,
  TrendingUp,
  Zap,
  AlertTriangle,
  CheckCircle2,
  PlayCircle,
  Lock,
  BookOpen,
  ArrowRight,
  Brain,
  Award,
  Flame,
  Activity,
  Cpu,
  HelpCircle,
} from "lucide-react";
import type { NodeItem } from "./CurriculumTree";

// ─── Types ────────────────────────────────────────────────────────────────────

interface DashboardOverviewProps {
  nodes: NodeItem[];
  onSelectNode: (id: string) => void;
  isLoadingNodes: boolean;
}

interface ProfileData {
  targetRole: string;
  baselineLevel: string;
  provider: string;
  userId: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getProfileFromStorage(): ProfileData {
  const provider = localStorage.getItem("aimos_provider") || "Not configured";
  const userId = localStorage.getItem("aimos_user_id") || "Guest";
  // Try to get profile from onboarding data if stored
  const storedProfile = localStorage.getItem("aimos_profile_matrix");
  if (storedProfile) {
    try {
      const parsed = JSON.parse(storedProfile);
      return {
        targetRole: parsed.target_role || "Software Engineer",
        baselineLevel: parsed.baseline_level || "Intermediate",
        provider,
        userId: userId.slice(0, 8),
      };
    } catch {/* ignore */}
  }
  return {
    targetRole: "Software Engineer",
    baselineLevel: "Intermediate",
    provider,
    userId: userId.slice(0, 8),
  };
}

// ─── Sub-components ───────────────────────────────────────────────────────────

const StatCard: React.FC<{
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  accent: string; // tailwind color token e.g. "indigo" | "emerald" | "amber" | "orange"
}> = ({ label, value, sub, icon, accent }) => {
  const accentMap: Record<string, { border: string; bg: string; text: string; subtext: string }> = {
    indigo: { border: "border-indigo-800/50", bg: "bg-indigo-950/30", text: "text-indigo-400", subtext: "text-indigo-300" },
    emerald: { border: "border-emerald-800/50", bg: "bg-emerald-950/30", text: "text-emerald-400", subtext: "text-emerald-300" },
    amber: { border: "border-amber-800/50", bg: "bg-amber-950/30", text: "text-amber-400", subtext: "text-amber-300" },
    orange: { border: "border-orange-800/50", bg: "bg-orange-950/30", text: "text-orange-400", subtext: "text-orange-300" },
    violet: { border: "border-violet-800/50", bg: "bg-violet-950/30", text: "text-violet-400", subtext: "text-violet-300" },
  };
  const c = accentMap[accent] || accentMap.indigo;

  return (
    <div className={`rounded-xl border ${c.border} ${c.bg} p-4 flex flex-col gap-1.5`}>
      <div className={`${c.text}`}>{icon}</div>
      <div className={`text-2xl font-bold text-slate-100 tabular-nums`}>{value}</div>
      <div className="text-xs font-semibold text-slate-200">{label}</div>
      {sub && <div className={`text-[10px] ${c.subtext} opacity-80`}>{sub}</div>}
    </div>
  );
};

const PhaseBar: React.FC<{
  phase: number;
  nodes: NodeItem[];
}> = ({ phase, nodes }) => {
  const phaseNodes = nodes.filter(n => n.phase === phase);
  const completed = phaseNodes.filter(n => n.status === "completed").length;
  const inProgress = phaseNodes.filter(n => n.status === "in_progress").length;
  const pct = phaseNodes.length > 0 ? Math.round(((completed + inProgress * 0.5) / phaseNodes.length) * 100) : 0;

  const phaseLabels: Record<number, string> = {
    1: "Foundations",
    2: "Java Core",
    3: "Collections & Data Structures",
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-slate-300">
          Phase {phase} — {phaseLabels[phase] || `Phase ${phase}`}
        </span>
        <span className="text-[10px] text-slate-500 tabular-nums">
          {completed}/{phaseNodes.length} complete
        </span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-indigo-400 transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
};

const WeakAreaItem: React.FC<{ node: NodeItem; onResume: (id: string) => void }> = ({ node, onResume }) => (
  <div className="flex items-center justify-between gap-3 rounded-lg border border-amber-900/30 bg-amber-950/15 px-3 py-2">
    <div className="flex items-center gap-2 min-w-0">
      <AlertTriangle size={12} className="text-amber-500 shrink-0" />
      <span className="text-xs text-slate-300 truncate">{node.title}</span>
      <span className="text-[9px] text-slate-500 shrink-0">Phase {node.phase}</span>
    </div>
    <button
      onClick={() => onResume(node.id)}
      className="shrink-0 rounded px-2 py-0.5 text-[10px] font-semibold text-amber-400 border border-amber-800/50 hover:bg-amber-950/40 transition-colors"
    >
      Revisit
    </button>
  </div>
);

// ─── Main Component ───────────────────────────────────────────────────────────

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  nodes,
  onSelectNode,
  isLoadingNodes,
}) => {
  const [profile] = useState<ProfileData>(getProfileFromStorage);
  const [backendPing, setBackendPing] = useState<"checking" | "online" | "offline">("checking");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showTutorial, setShowTutorial] = useState(!localStorage.getItem("aimos_hide_tutorial"));

  const toggleTutorial = () => {
    if (showTutorial) {
      localStorage.setItem("aimos_hide_tutorial", "true");
      setShowTutorial(false);
    } else {
      localStorage.removeItem("aimos_hide_tutorial");
      setShowTutorial(true);
    }
  };

  // Ping backend health
  useEffect(() => {
    fetch("http://localhost:8000/api/v1/curriculum/progress", {
      headers: { "X-User-Id": localStorage.getItem("aimos_user_id") || "" },
    })
      .then(r => r.ok ? setBackendPing("online") : setBackendPing("offline"))
      .catch(() => setBackendPing("offline"));
  }, []);

  // Live clock
  useEffect(() => {
    const id = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  // Derived stats
  const stats = useMemo(() => {
    const completed = nodes.filter(n => n.status === "completed").length;
    const inProgress = nodes.filter(n => n.status === "in_progress").length;
    const total = nodes.length;
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
    const weakAreas = nodes.filter(n => n.status === "in_progress" || n.status === "unlocked");
    const continueNode = nodes.find(n => n.status === "in_progress") || nodes.find(n => n.status === "unlocked");
    const phases = [...new Set(nodes.map(n => n.phase))].sort();
    return { completed, inProgress, total, pct, weakAreas, continueNode, phases };
  }, [nodes]);

  const providerDisplay = (p: string) => {
    const map: Record<string, string> = {
      "nvidia-nim": "NVIDIA NIM",
      "openai": "OpenAI GPT",
      "google-gemini": "Google Gemini",
      "anthropic": "Anthropic Claude",
    };
    return map[p] || p.toUpperCase();
  };

  return (
    <div className="flex h-full flex-col bg-slate-950 overflow-y-auto">

      {/* ── OS Identity Header ─────────────────────────────────────────────── */}
      <div className="border-b border-slate-800 bg-slate-900/60 px-6 py-4 shrink-0">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 p-2.5 shadow-lg shadow-indigo-950/60">
              <Brain size={20} className="text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-slate-100 tracking-tight">AI-MOS</h1>
                <span className="rounded-full bg-indigo-950/60 px-2 py-0.5 text-[9px] font-bold text-indigo-400 border border-indigo-800/50 uppercase tracking-widest">
                  v1.0 OS
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Artificial Intelligence Mentor Operating System
              </p>
            </div>
          </div>

          <div className="flex flex-col items-end gap-1.5">
            <div className="flex items-center gap-2">
              <button
                onClick={toggleTutorial}
                className="flex items-center gap-1 text-[9px] font-bold text-slate-400 hover:text-slate-200 border border-slate-800 rounded px-2 py-0.5 transition-all bg-slate-950/40"
                title="Toggle Platform Help Guide"
              >
                <HelpCircle size={10} />
                <span>{showTutorial ? "Hide Guide" : "Show Guide"}</span>
              </button>
              <div className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[9px] font-semibold border ${
                backendPing === "online"
                  ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/50"
                  : backendPing === "offline"
                    ? "bg-red-400/10 text-red-400 border-red-900/30"
                    : "bg-slate-800/60 text-slate-500 border-slate-700/50"
              }`}>
                <span className={`h-1.5 w-1.5 rounded-full ${
                  backendPing === "online" ? "bg-emerald-400 animate-pulse" : backendPing === "offline" ? "bg-red-400" : "bg-slate-500 animate-pulse"
                }`} />
                {backendPing === "online" ? "Core Services Online" : backendPing === "offline" ? "Backend Offline" : "Connecting…"}
              </div>
            </div>
            <span className="text-[10px] text-slate-600 tabular-nums">
              {currentTime.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
            </span>
          </div>
        </div>
      </div>

      <div className="flex-1 px-6 py-5 space-y-6">

        {/* ── Quick Start Guide Info Cards ─────────────────────────────────── */}
        {showTutorial && (
          <div className="rounded-xl border border-indigo-800/40 bg-slate-900/60 p-4 space-y-3 relative overflow-hidden transition-all duration-300">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Brain size={14} className="text-indigo-400" />
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Quick-Start Platform Utilities Guide
                </h2>
              </div>
              <button
                onClick={toggleTutorial}
                className="text-[10px] text-slate-500 hover:text-slate-300 border border-slate-800 hover:border-slate-700 rounded px-2 py-0.5 transition-colors"
              >
                Hide Guide
              </button>
            </div>

            <div className="grid grid-cols-3 gap-3">
              {/* Card 1: Navigation & Learning Path */}
              <div className="rounded-lg border border-slate-800/80 bg-slate-950/40 p-3 space-y-1.5 hover:border-indigo-500/30 transition-all hover:scale-[1.01]">
                <div className="flex items-center gap-1.5 text-indigo-400 font-semibold text-xs">
                  <LayoutDashboard size={13} />
                  <span>1. Navigation & Path</span>
                </div>
                <p className="text-[10px] text-slate-300 leading-relaxed">
                  Click any unlocked node in the left learning path to start. Review first-principles content, stories, and real-world analogies.
                </p>
              </div>

              {/* Card 2: Socratic Chat Console */}
              <div className="rounded-lg border border-slate-800/80 bg-slate-950/40 p-3 space-y-1.5 hover:border-violet-500/30 transition-all hover:scale-[1.01]">
                <div className="flex items-center gap-1.5 text-violet-400 font-semibold text-xs">
                  <Brain size={13} />
                  <span>2. Socratic Chat & Code Ban</span>
                </div>
                <p className="text-[10px] text-slate-300 leading-relaxed">
                  Discuss checkpoints in the Socratic chat console. If you fail understanding gates, our **Research Coach** locks code blocks to force muscle-memory typing!
                </p>
              </div>

              {/* Card 3: Srinivasan Interview Simulator */}
              <div className="rounded-lg border border-slate-800/80 bg-slate-950/40 p-3 space-y-1.5 hover:border-amber-500/30 transition-all hover:scale-[1.01]">
                <div className="flex items-center gap-1.5 text-amber-400 font-semibold text-xs">
                  <Target size={13} />
                  <span>3. Zoho Srinivasan Panel</span>
                </div>
                <p className="text-[10px] text-slate-300 leading-relaxed">
                  Toggle the tab in the right console to simulate a real, high-pressure Zoho mock interview. Get scored out of 10 and view active weaknesses.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ── Student Profile Banner ─────────────────────────────────────── */}
        <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-slate-900/80 to-indigo-950/20 p-4">
          <div className="flex items-center gap-2 mb-3">
            <Target size={14} className="text-indigo-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Student Mission Profile
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2">
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Target Role</div>
              <div className="text-sm font-semibold text-indigo-300">{profile.targetRole}</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Baseline Level</div>
              <div className="text-sm font-semibold text-slate-200">{profile.baselineLevel}</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Compute Provider</div>
              <div className="text-sm font-semibold text-violet-300">{providerDisplay(profile.provider)}</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">User Session</div>
              <div className="text-sm font-mono text-slate-400">{profile.userId}…</div>
            </div>
          </div>
        </div>

        {/* ── Stat Cards Row ─────────────────────────────────────────────── */}
        {isLoadingNodes ? (
          <div className="grid grid-cols-4 gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 animate-pulse h-24" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-4 gap-3">
            <StatCard
              label="Completed"
              value={stats.completed}
              sub={`of ${stats.total} nodes`}
              icon={<CheckCircle2 size={18} />}
              accent="emerald"
            />
            <StatCard
              label="In Progress"
              value={stats.inProgress}
              sub="active nodes"
              icon={<Activity size={18} />}
              accent="indigo"
            />
            <StatCard
              label="Completion"
              value={`${stats.pct}%`}
              sub="syllabus done"
              icon={<TrendingUp size={18} />}
              accent="violet"
            />
            <StatCard
              label="Weak Areas"
              value={stats.weakAreas.length}
              sub="need review"
              icon={<Flame size={18} />}
              accent="amber"
            />
          </div>
        )}

        {/* ── Overall Progress Bar ───────────────────────────────────────── */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp size={14} className="text-indigo-400" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Overall Syllabus Completion
              </h2>
            </div>
            <span className="text-lg font-bold text-indigo-300 tabular-nums">
              {stats.pct}%
            </span>
          </div>
          <div className="h-3 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-indigo-600 via-violet-500 to-indigo-400 transition-all duration-1000 ease-out relative"
              style={{ width: `${stats.pct}%` }}
            >
              <div className="absolute inset-0 bg-white/10 animate-pulse rounded-full" />
            </div>
          </div>

          {/* Phase breakdown */}
          {!isLoadingNodes && stats.phases.length > 0 && (
            <div className="space-y-2.5 pt-1">
              {stats.phases.map(phase => (
                <PhaseBar key={phase} phase={phase} nodes={nodes} />
              ))}
            </div>
          )}
        </div>

        {/* ── Two-column bottom section ──────────────────────────────────── */}
        <div className="grid grid-cols-2 gap-4">

          {/* Active Weak Areas */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-3">
            <div className="flex items-center gap-2">
              <AlertTriangle size={14} className="text-amber-400" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Active Weak Areas
              </h2>
            </div>

            {isLoadingNodes ? (
              <div className="space-y-2">
                {[1, 2].map(i => (
                  <div key={i} className="h-8 rounded-lg bg-slate-800 animate-pulse" />
                ))}
              </div>
            ) : stats.weakAreas.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-4 text-center space-y-1">
                <Award size={20} className="text-emerald-500" />
                <p className="text-xs text-emerald-400 font-semibold">No weak areas detected!</p>
                <p className="text-[10px] text-slate-500">All reviewed nodes are passing.</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {stats.weakAreas.slice(0, 5).map(node => (
                  <WeakAreaItem key={node.id} node={node} onResume={onSelectNode} />
                ))}
                {stats.weakAreas.length > 5 && (
                  <p className="text-[10px] text-slate-500 text-center">
                    +{stats.weakAreas.length - 5} more areas need attention
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Continue Learning Panel */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-3 flex flex-col">
            <div className="flex items-center gap-2">
              <Zap size={14} className="text-indigo-400" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Continue Learning
              </h2>
            </div>

            {isLoadingNodes ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-t-indigo-500 border-slate-800" />
              </div>
            ) : stats.continueNode ? (
              <div className="flex flex-col flex-1 gap-3">
                <div className="rounded-lg border border-indigo-800/40 bg-indigo-950/20 p-3 space-y-1">
                  <div className="flex items-center gap-1.5">
                    {stats.continueNode.status === "in_progress"
                      ? <PlayCircle size={12} className="text-indigo-400" />
                      : <BookOpen size={12} className="text-slate-400" />
                    }
                    <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                      {stats.continueNode.status === "in_progress" ? "In Progress" : "Next Up"}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-slate-100">{stats.continueNode.title}</p>
                  <p className="text-[10px] text-slate-500">Phase {stats.continueNode.phase}</p>
                </div>
                <button
                  onClick={() => onSelectNode(stats.continueNode!.id)}
                  className="mt-auto flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-2.5 text-xs font-bold text-white hover:from-indigo-500 hover:to-violet-500 transition-all shadow-lg shadow-indigo-950/50 group"
                >
                  Continue Learning
                  <ArrowRight size={13} className="transition-transform group-hover:translate-x-0.5" />
                </button>
              </div>
            ) : (
              <div className="flex flex-col flex-1 items-center justify-center text-center space-y-2 py-2">
                <Lock size={20} className="text-slate-600" />
                <p className="text-xs text-slate-500">All available nodes are locked.</p>
                <p className="text-[10px] text-slate-600">Complete current lessons to unlock more.</p>
              </div>
            )}
          </div>
        </div>

        {/* ── All Nodes Quick View ───────────────────────────────────────── */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-3">
          <div className="flex items-center gap-2">
            <LayoutDashboard size={14} className="text-indigo-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Syllabus Navigator
            </h2>
          </div>

          {isLoadingNodes ? (
            <div className="grid grid-cols-3 gap-2">
              {[...Array(9)].map((_, i) => (
                <div key={i} className="h-12 rounded-lg bg-slate-800 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-2">
              {nodes.map(node => {
                const statusStyles: Record<string, string> = {
                  completed: "border-emerald-800/40 bg-emerald-950/20 text-slate-300 cursor-pointer hover:bg-emerald-950/30",
                  in_progress: "border-indigo-700/50 bg-indigo-950/30 text-indigo-200 cursor-pointer hover:bg-indigo-950/50 ring-1 ring-indigo-700/30",
                  unlocked: "border-slate-700/50 bg-slate-800/30 text-slate-300 cursor-pointer hover:bg-slate-800/60",
                  locked: "border-slate-800/30 bg-slate-900/20 text-slate-600 cursor-not-allowed opacity-50",
                };
                const icons: Record<string, React.ReactNode> = {
                  completed: <CheckCircle2 size={10} className="text-emerald-400 shrink-0" />,
                  in_progress: <PlayCircle size={10} className="text-indigo-400 animate-pulse shrink-0" />,
                  unlocked: <BookOpen size={10} className="text-slate-400 shrink-0" />,
                  locked: <Lock size={10} className="text-slate-700 shrink-0" />,
                };
                return (
                  <button
                    key={node.id}
                    disabled={node.status === "locked"}
                    onClick={() => onSelectNode(node.id)}
                    className={`flex items-start gap-1.5 rounded-lg border px-2.5 py-2 text-left text-[10px] font-medium transition-all ${statusStyles[node.status] || statusStyles.locked}`}
                  >
                    <div className="mt-0.5">{icons[node.status]}</div>
                    <span className="leading-tight line-clamp-2">{node.title}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* ── System Info Footer ─────────────────────────────────────────── */}
        <div className="flex items-center justify-between text-[10px] text-slate-700 pb-2">
          <div className="flex items-center gap-1.5">
            <Cpu size={10} />
            <span>AI-MOS v1.0 — Java Developer Track</span>
          </div>
          <span>© 2025 Kuttiarun</span>
        </div>
      </div>
    </div>
  );
};
