import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { BookOpen, Check, Play, AlertCircle } from "lucide-react";
import { useTelemetry } from "../hooks/useTelemetry";

interface LessonCanvasProps {
  activeNodeId: string;
  onAdvanceNode: () => void;
}

export const LessonCanvas: React.FC<LessonCanvasProps> = ({
  activeNodeId,
  onAdvanceNode,
}) => {
  const { incrementAttempts, setTelemetryPassed } = useTelemetry(activeNodeId);
  const [markdown, setMarkdown] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Verification Form State
  const [submission, setSubmission] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [gateFeedback, setGateFeedback] = useState<string | null>(null);
  const [gatePassed, setGatePassed] = useState(false);

  // Fetch lesson markdown from the backend on node change
  useEffect(() => {
    const fetchLesson = async () => {
      setLoading(true);
      setError(null);
      setGatePassed(false);
      setGateFeedback(null);
      setSubmission("");

      try {
        const response = await fetch(`http://localhost:8000/api/v1/curriculum/node/${activeNodeId}`);
        if (!response.ok) {
          throw new Error(`Failed to load lesson (${response.status})`);
        }
        const data = await response.json();
        setMarkdown(data.content || "");
      } catch (err: any) {
        setError(err.message || "Could not retrieve curriculum contents.");
      } finally {
        setLoading(false);
      }
    };

    fetchLesson();
  }, [activeNodeId]);

  const handleValidateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!submission.trim() || isValidating) return;

    // Record this validation check attempt
    incrementAttempts();

    setIsValidating(true);
    setGateFeedback(null);

    // Read BYOK credentials from localStorage (same pattern as useLlmStream)
    const provider = localStorage.getItem("aimos_provider") || "nvidia-nim";
    const userId = localStorage.getItem("aimos_user_id");
    let apiKey = "";
    if (provider === "nvidia-nim") apiKey = localStorage.getItem("aimos_nvidia_api_key") || "";
    if (provider === "openai") apiKey = localStorage.getItem("aimos_openai_api_key") || "";
    if (provider === "google-gemini") apiKey = localStorage.getItem("aimos_gemini_api_key") || "";
    if (provider === "anthropic") apiKey = localStorage.getItem("aimos_anthropic_api_key") || "";

    try {
      const response = await fetch("http://localhost:8000/api/v1/curriculum/validate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-API-Key": apiKey,
          "X-User-Provider": provider,
          ...(userId ? { "X-User-Id": userId } : {}),
        },
        body: JSON.stringify({
          node_id: activeNodeId,
          submission_type: "explanation",
          user_text: submission.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Validation check failed.");
      }

      const data = await response.json();
      setGateFeedback(data.feedback);
      setGatePassed(data.passed);
      
      // Update telemetry passed status
      setTelemetryPassed(data.passed);
    } catch (err: any) {
      setGateFeedback(err.message || "An error occurred during verification.");
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-950 text-slate-100 select-text">
      {/* Header Bar */}
      <div className="flex items-center gap-2 border-b border-slate-800 p-4">
        <BookOpen size={16} className="text-indigo-400" />
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
          Knowledge Canvas
        </h2>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {loading ? (
          <div className="flex h-full items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-t-indigo-500 border-slate-800" />
          </div>
        ) : error ? (
          <div className="flex h-full items-center justify-center text-center p-6">
            <div>
              <AlertCircle size={32} className="mx-auto text-amber-500 mb-2" />
              <p className="text-sm text-slate-400 font-medium">{error}</p>
            </div>
          </div>
        ) : (
          <article className="prose prose-invert max-w-none text-sm leading-relaxed space-y-4 select-none">
            <ReactMarkdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                // Prevent lazy copying of code containers strictly (UI&UX.md §4)
                code({ node, className, children, ...props }) {
                  return (
                    <code
                      className={`${className} select-none bg-slate-900 px-1.5 py-0.5 rounded text-indigo-300 font-mono text-xs`}
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                pre({ children }) {
                  return (
                    <pre className="select-none bg-slate-900 border border-slate-800 rounded-lg p-4 font-mono text-xs text-indigo-200 overflow-x-auto">
                      {children}
                    </pre>
                  );
                },
                h1({ children }) {
                  return <h1 className="text-xl font-bold border-b border-slate-800 pb-2 text-indigo-400 mt-6 mb-4">{children}</h1>;
                },
                h2({ children }) {
                  return <h2 className="text-lg font-bold text-slate-200 mt-5 mb-2">{children}</h2>;
                },
                p({ children }) {
                  return <p className="text-slate-300 mb-4">{children}</p>;
                },
                ul({ children }) {
                  return <ul className="list-disc pl-5 space-y-1 mb-4 text-slate-400">{children}</ul>;
                },
                li({ children }) {
                  return <li className="text-slate-300">{children}</li>;
                },
              }}
            >
              {markdown}
            </ReactMarkdown>

            {/* Checkpoint Validation Gate Block */}
            <div className={`mt-8 rounded-xl border p-5 transition-all ${
              gatePassed 
                ? "border-emerald-500/50 bg-emerald-950/20" 
                : "border-slate-800 bg-slate-900/50"
            }`}>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                <Check className={gatePassed ? "text-emerald-400" : "text-slate-500"} size={16} />
                Verification Checkpoint Gate
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                In your own words, explain the core concepts of this lesson to the Socratic Mentor. 
                Your answer must be validated by the evaluation engine to unlock the next syllabus block.
              </p>

              {gateFeedback && (
                <div className={`mt-3 rounded-lg p-3 text-xs leading-relaxed ${
                  gatePassed 
                    ? "bg-emerald-950/30 text-emerald-300 border border-emerald-800/40" 
                    : "bg-amber-950/30 text-amber-300 border border-amber-800/40"
                }`}>
                  {gateFeedback}
                </div>
              )}

              {gatePassed ? (
                <button
                  onClick={onAdvanceNode}
                  className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-500 transition-colors shadow-md shadow-emerald-950/30"
                >
                  <Play size={12} />
                  Proceed to Next Lesson
                </button>
              ) : (
                <form onSubmit={handleValidateSubmit} className="mt-4 space-y-3">
                  <textarea
                    rows={3}
                    placeholder="Type your explanation here..."
                    required
                    value={submission}
                    onChange={(e) => setSubmission(e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-950 p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={isValidating || !submission.trim()}
                      className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors disabled:bg-slate-800 disabled:text-slate-500"
                    >
                      {isValidating ? "Evaluating..." : "Submit Answer"}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </article>
        )}
      </div>
    </div>
  );
};
