import React, { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Key, Cpu, AlertTriangle } from "lucide-react";
import { Message } from "../hooks/useLlmStream";

interface SocraticConsoleProps {
  messages: Message[];
  isStreaming: boolean;
  error: string | null;
  onSendMessage: (text: string) => void;
  onOpenKeys: () => void;
}

export const SocraticConsole: React.FC<SocraticConsoleProps> = ({
  messages,
  isStreaming,
  error,
  onSendMessage,
  onOpenKeys,
}) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const provider = localStorage.getItem("aimos_provider") || "None";
  const hasKey = !!localStorage.getItem("aimos_api_key");

  // Scroll to bottom when messages list updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim());
    setInput("");
  };

  return (
    <div className="flex h-full flex-col bg-slate-900 border-l border-slate-800 text-slate-100 select-text">
      {/* Console Header */}
      <div className="flex items-center justify-between border-b border-slate-800 p-4">
        <div className="flex items-center gap-2">
          <Cpu className={isStreaming ? "text-indigo-400 animate-spin" : "text-indigo-400"} size={16} />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Socratic Mentor
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
                  components={{
                    // Format output code tags nicely
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
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              )}
            </div>
          ))
        )}

        {/* Streaming Placeholder indicator */}
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
  );
};
