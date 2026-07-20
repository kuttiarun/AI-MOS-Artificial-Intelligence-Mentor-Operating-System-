import React, { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import remarkGfm from "remark-gfm";
import rehypeKatex from "rehype-katex";
import { Send, Key, Cpu, AlertTriangle, Flame, Award, ChevronDown, ChevronRight, Info } from "lucide-react";
import type { Message } from "../hooks/useLlmStream";

interface SocraticConsoleProps {
  messages: Message[];
  isStreaming: boolean;
  error: string | null;
  onSendMessage: (text: string) => void;
  onOpenKeys: () => void;
  activeNodeId: string;
  weakAreaCount?: number;
}

export const SocraticConsole: React.FC<SocraticConsoleProps> = ({
  messages,
  isStreaming,
  error,
  onSendMessage,
  onOpenKeys,
  activeNodeId,
  weakAreaCount = 0,
}) => {
  const [activeTab, setActiveTab] = useState<"socratic" | "interview">("socratic");
  const [input, setInput] = useState("");
  const [contextInspectorOpen, setContextInspectorOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const interviewEndRef = useRef<HTMLDivElement>(null);

  // Zoho Interview Simulator States
  const [interviewActive, setInterviewActive] = useState(false);
  const [interviewMessages, setInterviewMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [interviewInput, setInterviewInput] = useState("");
  const [isInterviewLoading, setIsInterviewLoading] = useState(false);
  const [latestScore, setLatestScore] = useState<number | null>(null);
  const [latestCritique, setLatestCritique] = useState<string | null>(null);
  const [interviewError, setInterviewError] = useState<string | null>(null);

  const provider = localStorage.getItem("aimos_provider") || "None";
  const hasKey = !!localStorage.getItem("aimos_api_key");

  // Scroll to bottom when messages list updates
  useEffect(() => {
    if (activeTab === "socratic") {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    } else {
      interviewEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, interviewMessages, isStreaming, isInterviewLoading, activeTab]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleStartInterview = async () => {
    setInterviewError(null);
    setIsInterviewLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/interview/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) {
        throw new Error(`Failed to start interview: status ${response.status}`);
      }
      const data = await response.json();
      setInterviewMessages([
        { role: "assistant", content: `${data.initial_question}` }
      ]);
      setInterviewActive(true);
      setLatestScore(null);
      setLatestCritique(null);
    } catch (err: any) {
      setInterviewError(err.message || "Could not start the Zoho interview session.");
    } finally {
      setIsInterviewLoading(false);
    }
  };

  // Auto-activate Zoho mock interview session when user switches to Zoho panel tab
  useEffect(() => {
    if (activeTab === "interview" && !interviewActive && interviewMessages.length === 0 && !isInterviewLoading) {
      handleStartInterview();
    }
  }, [activeTab, interviewActive, interviewMessages, isInterviewLoading]);

  // Reset interview state when active node changes
  useEffect(() => {
    setInterviewActive(false);
    setInterviewMessages([]);
    setLatestScore(null);
    setLatestCritique(null);
    setInterviewError(null);
  }, [activeNodeId]);

  const handleSendInterviewMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!interviewInput.trim() || isInterviewLoading) return;

    const apiKey = localStorage.getItem("aimos_api_key") || "";
    const providerHeader = localStorage.getItem("aimos_provider") || "";
    const userId = localStorage.getItem("aimos_user_id") || "";

    if (!apiKey) {
      setInterviewError("API key configuration is missing. Configure keys first.");
      return;
    }

    const candidateAnswer = interviewInput.trim();
    setInterviewInput("");
    
    // Append candidate answer to conversation history
    const userTurn = { role: "user" as const, content: candidateAnswer };
    const updatedMessages = [...interviewMessages, userTurn];
    setInterviewMessages(updatedMessages);
    setIsInterviewLoading(true);
    setInterviewError(null);

    try {
      const response = await fetch("http://localhost:8000/api/v1/interview/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-API-Key": apiKey,
          "X-User-Provider": providerHeader,
          ...(userId ? { "X-User-Id": userId } : {}),
        },
        body: JSON.stringify({
          node_id: activeNodeId,
          candidate_answer: candidateAnswer,
          chat_history: interviewMessages, // Send previous turns as context dynamically
        }),
      });

      if (!response.ok) {
        throw new Error(`Upstream error: status ${response.status}`);
      }

      const data = await response.json();
      setLatestScore(data.score);
      setLatestCritique(data.critique);

      // Append Srinivasan's feedback and next question
      const assistantTurn = {
        role: "assistant" as const,
        content: `**Srinivasan's Question:**\n\n${data.next_question}`,
      };
      setInterviewMessages((prev) => [...prev, assistantTurn]);
    } catch (err: any) {
      setInterviewError(err.message || "Failed to process interview response.");
    } finally {
      setIsInterviewLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-900 border-l border-slate-800 text-slate-100 select-text">
      {/* Console Header */}
      <div className="flex items-center justify-between border-b border-slate-800 p-4">
        <div className="flex items-center gap-2">
          <Cpu className={isStreaming ? "text-indigo-400 animate-spin" : "text-indigo-400"} size={16} />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Compute Hub
          </h2>
        </div>

        <div className="flex items-center gap-2">
          {/* Connection Pill */}
          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[9px] font-medium border ${
            hasKey 
              ? "bg-emerald-950/30 text-emerald-400 border-emerald-800/40" 
              : "bg-amber-950/30 text-amber-400 border-amber-800/40"
          }`}>
            <span className={`h-1 w-1 rounded-full ${hasKey ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
            {hasKey ? `${provider.toUpperCase()} Connected` : "Keys Config Required"}
          </span>

          {/* BYOK Settings Trigger */}
          <button
            onClick={onOpenKeys}
            className="rounded-lg border border-slate-800 p-1.5 text-slate-400 hover:bg-slate-950 hover:text-slate-100 transition-colors"
            title="Configure API Keys"
          >
            <Key size={14} />
          </button>
        </div>
      </div>

      {/* Tabs Layout */}
      <div className="flex border-b border-slate-800 bg-slate-950/40">
        <button
          onClick={() => setActiveTab("socratic")}
          className={`flex-1 py-2.5 text-center text-[10px] font-bold uppercase tracking-wider transition-all ${
            activeTab === "socratic"
              ? "border-b-2 border-indigo-500 text-indigo-400 bg-slate-900/50"
              : "text-slate-500 hover:text-slate-300"
          }`}
        >
          Socratic Mentor
        </button>
        <button
          onClick={() => setActiveTab("interview")}
          className={`flex-1 py-2.5 text-center text-[10px] font-bold uppercase tracking-wider transition-all ${
            activeTab === "interview"
              ? "border-b-2 border-orange-500 text-orange-400 bg-slate-900/50"
              : "text-slate-500 hover:text-slate-300"
          }`}
        >
          Zoho Panel (Srinivasan)
        </button>
      </div>

      {/* Context Inspector Badge */}
      <div className="border-b border-slate-800 bg-slate-950/60 shrink-0">
        <button
          onClick={() => setContextInspectorOpen(o => !o)}
          className="flex w-full items-center justify-between px-4 py-2 text-[10px] text-slate-500 hover:text-slate-300 transition-colors"
        >
          <div className="flex items-center gap-1.5">
            <Info size={10} className="text-indigo-500" />
            <span className="font-semibold uppercase tracking-wider">Context Inspector</span>
          </div>
          {contextInspectorOpen
            ? <ChevronDown size={11} />
            : <ChevronRight size={11} />}
        </button>

        {contextInspectorOpen && (
          <div className="grid grid-cols-3 gap-px bg-slate-800 border-t border-slate-800">
            <div className="bg-slate-950/80 px-3 py-2 space-y-0.5">
              <div className="text-[9px] uppercase tracking-widest text-slate-600 font-semibold">Active Node</div>
              <div className="text-[10px] font-mono text-indigo-400 truncate" title={activeNodeId}>{activeNodeId}</div>
            </div>
            <div className="bg-slate-950/80 px-3 py-2 space-y-0.5">
              <div className="text-[9px] uppercase tracking-widest text-slate-600 font-semibold">Provider</div>
              <div className="text-[10px] text-violet-400 truncate">{provider === "None" ? "Not set" : provider.toUpperCase()}</div>
            </div>
            <div className="bg-slate-950/80 px-3 py-2 space-y-0.5">
              <div className="text-[9px] uppercase tracking-widest text-slate-600 font-semibold">Weak Areas</div>
              <div className={`text-[10px] font-bold ${weakAreaCount > 0 ? "text-amber-400" : "text-emerald-400"}`}>
                {weakAreaCount > 0 ? `${weakAreaCount} flagged` : "None detected"}
              </div>
            </div>
          </div>
        )}
      </div>
      {activeTab === "socratic" && (
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Chat Messages Log */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-center p-6 space-y-2">
                <Cpu size={24} className="text-slate-700" />
                <p className="text-xs text-slate-500 font-medium max-w-[200px]">
                  Ask your first question about the lesson to activate the Socratic Mentor.
                </p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex flex-col max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed ${
                    msg.role === "user"
                      ? "ml-auto bg-indigo-600 text-white rounded-tr-none"
                      : "bg-slate-950 text-slate-300 border border-slate-800/80 rounded-tl-none prose prose-invert prose-xs"
                  }`}
                >
                  {msg.role === "user" ? (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkMath, remarkGfm]}
                      rehypePlugins={[rehypeKatex]}
                      components={{
                        code({ className, children, ...props }) {
                          return (
                            <code
                              className={`${className} bg-slate-900 px-1 py-0.5 rounded text-indigo-300 font-mono text-[10px]`}
                              {...props}
                            >
                              {children}
                            </code>
                          );
                        },
                        pre({ children }) {
                          return (
                            <pre className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 my-1.5 font-mono text-[10px] text-indigo-200 overflow-x-auto">
                              {children}
                            </pre>
                          );
                        },
                        p({ children }) {
                          return <p className="mb-1.5 last:mb-0">{children}</p>;
                        },
                        ul({ children }) {
                          return <ul className="list-disc pl-4 space-y-0.5 my-1 text-slate-400">{children}</ul>;
                        },
                        table({ children }) {
                          return (
                            <div className="overflow-x-auto my-3 rounded-lg border border-slate-800 bg-slate-900/10">
                              <table className="w-full text-left border-collapse text-[10px]">
                                {children}
                              </table>
                            </div>
                          );
                        },
                        thead({ children }) {
                          return <thead className="bg-slate-900 text-slate-200 border-b border-slate-800 font-semibold">{children}</thead>;
                        },
                        tbody({ children }) {
                          return <tbody className="divide-y divide-slate-800">{children}</tbody>;
                        },
                        tr({ children }) {
                          return <tr className="even:bg-slate-900/30 hover:bg-slate-900/50 transition-colors">{children}</tr>;
                        },
                        th({ children }) {
                          return <th className="px-3 py-2 font-bold border-r border-slate-800 last:border-r-0">{children}</th>;
                        },
                        td({ children }) {
                          return <td className="px-3 py-1.5 text-slate-300 border-r border-slate-800 last:border-r-0">{children}</td>;
                        },
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
              ))
            )}

            {/* Streaming Placeholder */}
            {isStreaming && messages[messages.length - 1]?.role !== "mentor" && (
              <div className="flex max-w-[85%] rounded-xl rounded-tl-none bg-slate-950 border border-slate-800/80 px-3 py-2 text-xs text-slate-500">
                <span className="flex gap-1 items-center">
                  <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce" />
                  <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                </span>
              </div>
            )}

            {/* Global Error Banner */}
            {error && (
              <div className="flex gap-2 rounded-lg border border-red-900/40 bg-red-950/20 p-3 text-xs text-red-300 border-red-950/30">
                <AlertTriangle className="shrink-0 text-red-400" size={16} />
                <p>{error}</p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Area */}
          <div className="border-t border-slate-800 p-3 bg-slate-950/50">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                placeholder={
                  hasKey 
                    ? "Ask the Socratic Mentor a question..." 
                    : "Configure API Keys to chat"
                }
                disabled={!hasKey || isStreaming}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming || !hasKey}
                className="rounded-lg bg-indigo-600 p-2 text-white hover:bg-indigo-500 transition-colors disabled:bg-slate-800 disabled:text-slate-500 shadow-md shadow-indigo-950/40"
              >
                <Send size={14} />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Tab Contents: Zoho Mock Interview */}
      {activeTab === "interview" && (
        <div className="flex flex-1 flex-col overflow-hidden">
          {!interviewActive ? (
            <div className="flex flex-1 flex-col items-center justify-center text-center p-6 space-y-4">
              <div className="rounded-full bg-orange-950/40 p-4 border border-orange-800/40 text-orange-400 animate-pulse">
                <Flame size={28} />
              </div>
              <div className="space-y-2">
                <h3 className="text-sm font-bold text-slate-100">Zoho Mock Interview Panel</h3>
                <p className="text-xs text-slate-400 max-w-[260px] leading-relaxed mx-auto">
                  Face <strong className="text-orange-400">Srinivasan</strong>, a Senior Architect on the Zoho Java compiler core team.
                  Prepare to defend GC choices, HashMap layouts, and vtable dispatch.
                </p>
                <p className="text-[10px] text-amber-500 bg-amber-950/20 border border-amber-900/30 rounded-lg p-2 max-w-[240px] mx-auto">
                  ⚠️ Scores below 6/10 write active failure records directly to your syllabus progress metrics.
                </p>
              </div>
              <button
                onClick={handleStartInterview}
                disabled={isInterviewLoading}
                className="rounded-lg bg-orange-600 hover:bg-orange-500 px-6 py-2.5 text-xs font-semibold text-white transition-all shadow-lg shadow-orange-950/50"
              >
                {isInterviewLoading ? "Connecting..." : "Begin High-Pressure Session"}
              </button>
              {interviewError && (
                <div className="flex gap-2 rounded-lg border border-red-900/40 bg-red-950/20 p-3 text-xs text-red-300">
                  <AlertTriangle className="shrink-0 text-red-400" size={16} />
                  <p>{interviewError}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-1 flex-col overflow-hidden">
              {/* Interview message log */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {interviewMessages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex flex-col max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed ${
                      msg.role === "user"
                        ? "ml-auto bg-orange-600 text-white rounded-tr-none"
                        : "bg-slate-950 text-slate-300 border border-slate-800/80 rounded-tl-none prose prose-invert prose-xs select-text"
                    }`}
                  >
                    {msg.role === "user" ? (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <ReactMarkdown
                        remarkPlugins={[remarkMath, remarkGfm]}
                        rehypePlugins={[rehypeKatex]}
                        components={{
                          code({ className, children, ...props }) {
                            return (
                              <code
                                className={`${className} bg-slate-900 px-1 py-0.5 rounded text-orange-300 font-mono text-[10px]`}
                                {...props}
                              >
                                {children}
                              </code>
                            );
                          },
                          pre({ children }) {
                            return (
                              <pre className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 my-1.5 font-mono text-[10px] text-orange-200 overflow-x-auto">
                                {children}
                              </pre>
                            );
                          },
                          p({ children }) {
                            return <p className="mb-1.5 last:mb-0">{children}</p>;
                          },
                          table({ children }) {
                            return (
                              <div className="overflow-x-auto my-3 rounded-lg border border-slate-800 bg-slate-900/10">
                                <table className="w-full text-left border-collapse text-[10px]">
                                  {children}
                                </table>
                              </div>
                            );
                          },
                          thead({ children }) {
                            return <thead className="bg-slate-900 text-slate-200 border-b border-slate-800 font-semibold">{children}</thead>;
                          },
                          tbody({ children }) {
                            return <tbody className="divide-y divide-slate-800">{children}</tbody>;
                          },
                          tr({ children }) {
                            return <tr className="even:bg-slate-900/30 hover:bg-slate-900/50 transition-colors">{children}</tr>;
                          },
                          th({ children }) {
                            return <th className="px-3 py-2 font-bold border-r border-slate-800 last:border-r-0">{children}</th>;
                          },
                          td({ children }) {
                            return <td className="px-3 py-1.5 text-slate-300 border-r border-slate-800 last:border-r-0">{children}</td>;
                          },
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    )}
                  </div>
                ))}

                {isInterviewLoading && (
                  <div className="flex max-w-[85%] rounded-xl rounded-tl-none bg-slate-950 border border-slate-800/80 px-3 py-2 text-xs text-slate-500">
                    <span className="flex gap-1 items-center">
                      <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce" />
                      <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                      <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                    </span>
                    <span className="ml-2 text-[10px] text-slate-500">Srinivasan is analyzing depth...</span>
                  </div>
                )}

                {interviewError && (
                  <div className="flex gap-2 rounded-lg border border-red-900/40 bg-red-950/20 p-3 text-xs text-red-300">
                    <AlertTriangle className="shrink-0 text-red-400" size={16} />
                    <p>{interviewError}</p>
                  </div>
                )}

                <div ref={interviewEndRef} />
              </div>

              {/* Latest score panel if evaluated */}
              {latestScore !== null && (
                <div className={`mx-4 mb-2 p-3 rounded-lg border text-xs leading-relaxed ${
                  latestScore >= 6 
                    ? "bg-emerald-950/20 border-emerald-800/50 text-emerald-300"
                    : "bg-red-950/20 border-red-900/50 text-red-300"
                }`}>
                  <div className="flex items-center justify-between font-semibold border-b border-slate-800 pb-1 mb-1">
                    <span className="flex items-center gap-1">
                      <Award size={14} className={latestScore >= 6 ? "text-emerald-400" : "text-red-400"} />
                      Srinivasan's Evaluation
                    </span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      latestScore >= 6 ? "bg-emerald-900/50 text-emerald-300" : "bg-red-900/50 text-red-300"
                    }`}>
                      Score: {latestScore}/10 ({latestScore >= 6 ? "PASSED" : "FAILED"})
                    </span>
                  </div>
                  <p className="mt-1">{latestCritique}</p>
                </div>
              )}

              {/* Chat Input Area */}
              <div className="border-t border-slate-800 p-3 bg-slate-950/50">
                <form onSubmit={handleSendInterviewMessage} className="flex gap-2">
                  <input
                    type="text"
                    placeholder={
                      hasKey 
                        ? "Type your high-pressure response..." 
                        : "Configure API Keys to begin"
                    }
                    disabled={isInterviewLoading || !hasKey}
                    value={interviewInput}
                    onChange={(e) => setInterviewInput(e.target.value)}
                    className="flex-1 rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-orange-500 disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={!interviewInput.trim() || isInterviewLoading || !hasKey}
                    className="rounded-lg bg-orange-600 p-2 text-white hover:bg-orange-500 transition-colors disabled:bg-slate-800 disabled:text-slate-500 shadow-md shadow-orange-950/40"
                  >
                    <Send size={14} />
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
