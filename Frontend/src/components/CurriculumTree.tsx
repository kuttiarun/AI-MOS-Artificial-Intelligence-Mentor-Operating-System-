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
  // Phase 4: Java Advanced
  { id: "java-advanced-exceptions", title: "Exception Handling", phase: 4, status: "locked" },
  { id: "java-advanced-generics", title: "Generics & Wildcards", phase: 4, status: "locked" },
  { id: "java-advanced-streams", title: "Streams API", phase: 4, status: "locked" },
  { id: "java-advanced-lambda", title: "Lambda & Functional", phase: 4, status: "locked" },
  { id: "java-advanced-concurrency", title: "Concurrency & Threads", phase: 4, status: "locked" },
  { id: "java-advanced-jvm-memory", title: "JVM Memory & GC", phase: 4, status: "locked" },
  // Phase 5: Testing
  { id: "testing-junit5", title: "JUnit 5 Unit Tests", phase: 5, status: "locked" },
  { id: "testing-mockito", title: "Mockito & Mocking", phase: 5, status: "locked" },
  { id: "testing-integration", title: "Integration Testing", phase: 5, status: "locked" },
  { id: "testing-tdd", title: "TDD Cycle", phase: 5, status: "locked" },
  { id: "testing-coverage", title: "Test Coverage & JaCoCo", phase: 5, status: "locked" },
  // Phase 6: Backend/Spring Boot
  { id: "spring-intro", title: "Spring Boot Intro", phase: 6, status: "locked" },
  { id: "spring-mvc", title: "Spring MVC & REST", phase: 6, status: "locked" },
  { id: "spring-data-jpa", title: "Spring Data JPA", phase: 6, status: "locked" },
  { id: "spring-rest-design", title: "REST API Design", phase: 6, status: "locked" },
  { id: "spring-security", title: "Spring Security & JWT", phase: 6, status: "locked" },
  { id: "spring-deployment", title: "Docker & Deployment", phase: 6, status: "locked" },
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

  const phases = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  const phaseConfig: Record<number, { label: string; color: string; dot: string }> = {
    1: { label: "Foundations",       color: "text-slate-400",   dot: "bg-slate-500" },
    2: { label: "Java Core",         color: "text-blue-400",    dot: "bg-blue-500" },
    3: { label: "Collections & DS",  color: "text-indigo-400",  dot: "bg-indigo-500" },
    4: { label: "Java Advanced",     color: "text-amber-400",   dot: "bg-amber-500" },
    5: { label: "Testing",           color: "text-teal-400",    dot: "bg-teal-500" },
    6: { label: "Backend / Spring",  color: "text-rose-400",    dot: "bg-rose-500" },
    7: { label: "Build & Database",  color: "text-cyan-400",    dot: "bg-cyan-500" },
    8: { label: "Design Patterns",   color: "text-purple-400",  dot: "bg-purple-500" },
    9: { label: "System & Cloud",    color: "text-emerald-400", dot: "bg-emerald-500" },
    10: { label: "DSA Interviews",   color: "text-orange-400",  dot: "bg-orange-500" },
  };

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
        {phases.map((phase) => {
          const phaseNodes = nodes.filter((node) => node.phase === phase);
          if (phaseNodes.length === 0) return null;
          const cfg = phaseConfig[phase];
          return (
            <div key={phase} className="space-y-1.5">
              <div className="flex items-center gap-1.5 px-2">
                <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
                <h4 className={`text-[9px] font-bold uppercase tracking-widest ${cfg.color}`}>
                  Ph.{phase} — {cfg.label}
                </h4>
              </div>

              <div className="space-y-1">
                {phaseNodes.map((node) => {
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
          );
        })}
      </div>
    </div>
  );
};
