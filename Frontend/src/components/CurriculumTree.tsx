import React from "react";
import { Lock, CheckCircle2, PlayCircle, BookOpen } from "lucide-react";

export interface NodeItem {
  id: string;
  title: string;
  phase: number;
  status: "locked" | "unlocked" | "in_progress" | "completed";
}

interface CurriculumTreeProps {
  activeNodeId: string;
  onSelectNode: (id: string) => void;
}

// Full Java study roadmap matching initial schema migration seeds
const CURRICULUM_ROADMAP: NodeItem[] = [
  // Phase 1: Foundations
  { id: "foundations-intro", title: "Intro to SE", phase: 1, status: "completed" },
  { id: "foundations-how-computers-work", title: "How CPUs Work", phase: 1, status: "completed" },
  { id: "foundations-programming-basics", title: "Programming Logic", phase: 1, status: "completed" },
  // Phase 2: Java Core
  { id: "java-core-setup", title: "Java Setup & JVM", phase: 2, status: "completed" },
  { id: "java-core-oop-classes", title: "Classes & Objects", phase: 2, status: "completed" },
  { id: "java-core-oop-inheritance", title: "OOP Inheritance", phase: 2, status: "completed" },
  { id: "java-core-interface", title: "Interfaces", phase: 2, status: "in_progress" },
  { id: "java-core-abstract-class", title: "Abstract Classes", phase: 2, status: "unlocked" },
  // Phase 3: Java Collections
  { id: "java-collections-arrays", title: "Arrays & Memory", phase: 3, status: "unlocked" },
  { id: "java-collections-arraylist", title: "ArrayList Internals", phase: 3, status: "locked" },
  { id: "java-collections-linkedlist", title: "LinkedList Nodes", phase: 3, status: "locked" },
  { id: "java-collections-hashmap", title: "HashMap Buckets", phase: 3, status: "locked" },
];

export const CurriculumTree: React.FC<CurriculumTreeProps> = ({
  activeNodeId,
  onSelectNode,
}) => {
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
        <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
          Learning Path
        </h3>
        <p className="text-[10px] text-slate-500 mt-0.5">Java Developer Syllabus</p>
      </div>

      {/* Nodes list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {phases.map((phase) => (
          <div key={phase} className="space-y-1.5">
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2">
              Phase {phase}
            </h4>

            <div className="space-y-1">
              {CURRICULUM_ROADMAP.filter((node) => node.phase === phase).map((node) => {
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
