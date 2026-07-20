import React, { useState, useEffect, useCallback } from "react";
import { Lock, CheckCircle2, PlayCircle, BookOpen, RefreshCw, LayoutDashboard } from "lucide-react";

export interface NodeItem {
  id: string;
  title: string;
  phase: number;
  status: "locked" | "unlocked" | "in_progress" | "completed";
}

interface CurriculumTreeProps {
  activeNodeId: string;
  onSelectNode: (id: string) => void;
  onGoHome: () => void;
  isDashboardActive: boolean;
}

// Fallback roadmap used only when the backend is unreachable (dev offline mode)
const FALLBACK_ROADMAP: NodeItem[] = [
  // Phase 1: Foundations
  { id: "foundations-intro", title: "Intro to SE", phase: 1, status: "locked" },
  { id: "foundations-how-computers-work", title: "How CPUs Work", phase: 1, status: "locked" },
  { id: "foundations-programming-basics", title: "Programming Logic", phase: 1, status: "locked" },
  // Phase 2: Java Core
  { id: "java-core-setup", title: "Java Setup & JVM", phase: 2, status: "locked" },
  { id: "java-core-oop-classes", title: "Classes & Objects", phase: 2, status: "locked" },
  { id: "java-core-oop-inheritance", title: "OOP Inheritance", phase: 2, status: "locked" },
  { id: "java-core-interface", title: "Interfaces", phase: 2, status: "in_progress" },
  { id: "java-core-abstract-class", title: "Abstract Classes", phase: 2, status: "locked" },
  // Phase 3: Java Collections
  { id: "java-collections-arrays", title: "Arrays & Memory", phase: 3, status: "locked" },
  { id: "java-collections-arraylist", title: "ArrayList Internals", phase: 3, status: "locked" },
  { id: "java-collections-linkedlist", title: "LinkedList Nodes", phase: 3, status: "locked" },
  { id: "java-collections-hashmap", title: "HashMap Buckets", phase: 3, status: "locked" },
];

export const CurriculumTree: React.FC<CurriculumTreeProps> = ({
  activeNodeId,
  onSelectNode,
  onGoHome,
  isDashboardActive,
}) => {
  const [nodes, setNodes] = useState<NodeItem[]>(FALLBACK_ROADMAP);
  const [isLoading, setIsLoading] = useState(true);

  const fetchProgress = useCallback(async () => {
    setIsLoading(true);
    const userId = localStorage.getItem("aimos_user_id");
    try {
      const response = await fetch("http://localhost:8000/api/v1/curriculum/progress", {
        headers: {
          ...(userId ? { "X-User-Id": userId } : {}),
        },
      });
      if (response.ok) {
        const data: NodeItem[] = await response.json();
        setNodes(data);
      }
      // If not OK (e.g. DB not connected), keep the fallback silently
    } catch {
      // Backend unreachable — fallback roadmap stays in place
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  // Re-fetch whenever the active node changes (a validation pass may have unlocked a new node)
  useEffect(() => {
    fetchProgress();
  }, [activeNodeId, fetchProgress]);

  const phases = [1, 2, 3];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="text-emerald-400 shrink-0" size={14} />;
      case "in_progress":
        return <PlayCircle className="text-indigo-400 animate-pulse shrink-0" size={14} />;
      case "unlocked":
        return <BookOpen className="text-slate-400 shrink-0" size={14} />;
      case "locked":
      default:
        return <Lock className="text-slate-600 shrink-0" size={14} />;
    }
  };

  const getStatusStyle = (status: string, isActive: boolean) => {
    if (isActive) return "bg-indigo-950/40 border border-indigo-800 text-indigo-100";
    switch (status) {
      case "locked":
        return "text-slate-500 opacity-60 cursor-not-allowed";
      case "completed":
        return "text-slate-300 hover:bg-slate-900/50 hover:text-slate-200 cursor-pointer";
      default:
        return "text-slate-100 hover:bg-slate-900/50 cursor-pointer";
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-900/80 border-r border-slate-800 text-slate-100 select-none">
      {/* Title Header */}
      <div className="border-b border-slate-800 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
              Learning Path
            </h3>
            <p className="text-[10px] text-slate-500 mt-0.5">Java Developer Syllabus</p>
          </div>
          {/* Refresh button */}
          <button
            onClick={fetchProgress}
            disabled={isLoading}
            className="rounded p-1 text-slate-600 hover:text-slate-400 transition-colors"
            title="Refresh progress"
          >
            <RefreshCw size={12} className={isLoading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {/* Dashboard Home Button */}
      <div className="px-3 pt-3 pb-1">
        <button
          onClick={onGoHome}
          className={`flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-left text-xs font-semibold transition-all ${
            isDashboardActive
              ? "bg-indigo-950/60 border border-indigo-700/50 text-indigo-300"
              : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
          }`}
        >
          <LayoutDashboard size={14} className={isDashboardActive ? "text-indigo-400" : "text-slate-500"} />
          <span>OS Dashboard</span>
        </button>
      </div>

      {/* Nodes list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {phases.map((phase) => (
          <div key={phase} className="space-y-1.5">
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2">
              Phase {phase}
            </h4>

            <div className="space-y-1">
              {nodes.filter((node) => node.phase === phase).map((node) => {
                const isActive = node.id === activeNodeId;
                const isLocked = node.status === "locked";

                return (
                  <button
                    key={node.id}
                    disabled={isLocked}
                    onClick={() => onSelectNode(node.id)}
                    className={`flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-left text-xs font-medium transition-all ${getStatusStyle(
                      node.status,
                      isActive
                    )}`}
                  >
                    {getStatusIcon(node.status)}
                    <span className="truncate">{node.title}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
