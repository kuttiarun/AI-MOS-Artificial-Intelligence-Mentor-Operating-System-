import { useState, useEffect, useRef } from "react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface OnboardingMessage {
  role: "assistant" | "user";
  content: string;
}

interface OnboardingChatProps {
  onComplete: () => void;
  onOpenKeys?: () => void;
}

// ─── API Helpers ──────────────────────────────────────────────────────────────

const API_BASE = "http://localhost:8000/api/v1/onboarding";

function getAuthHeaders(): Record<string, string> {
  const provider = localStorage.getItem("aimos_provider") || "nvidia-nim";
  const userId = localStorage.getItem("aimos_user_id");
  let apiKey = "";
  if (provider === "nvidia-nim") apiKey = localStorage.getItem("aimos_nvidia_api_key") || "";
  if (provider === "google-gemini") apiKey = localStorage.getItem("aimos_gemini_api_key") || "";
  if (provider === "anthropic") apiKey = localStorage.getItem("aimos_anthropic_api_key") || "";
  if (provider === "openai") apiKey = localStorage.getItem("aimos_openai_api_key") || "";

  return {
    "Content-Type": "application/json",
    "X-User-API-Key": apiKey,
    "X-User-Provider": provider,
    ...(userId ? { "X-User-Id": userId } : {}),
  };
}

// ─── Component ────────────────────────────────────────────────────────────────

export function OnboardingChat({ onComplete, onOpenKeys }: OnboardingChatProps) {
  const [messages, setMessages] = useState<OnboardingMessage[]>([]);
  const [input, setInput] = useState("");
  const [turnNumber, setTurnNumber] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const chatLogRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages update
  useEffect(() => {
    const log = chatLogRef.current;
    if (log) {
      log.scrollTo({ top: log.scrollHeight, behavior: "smooth" });
    }
  }, [messages, isLoading, isFinishing]);

  // On mount: call /start to get opening message
  useEffect(() => {
    const init = async () => {
      try {
        const res = await fetch(`${API_BASE}/start`, { method: "POST" });
        const data = await res.json();
        setMessages([{ role: "assistant", content: data.opening_message }]);
        setTurnNumber(1);
      } catch {
        setError("Failed to connect to the AI-MOS server. Please ensure the backend is running.");
      } finally {
        setIsLoading(false);
      }
    };
    init();
  }, []);

  // Focus input when loading finishes
  useEffect(() => {
    if (!isLoading && !isFinishing) inputRef.current?.focus();
  }, [isLoading, isFinishing]);

  const handleSend = async () => {
    if (!input.trim() || isSending || isFinishing || turnNumber === 0) return;

    // Client-side credentials check to prevent protocol errors
    const headers = getAuthHeaders();
    if (!headers["X-User-API-Key"]) {
      setError("API key configuration is missing. Click the key icon in the top right to configure credentials.");
      return;
    }

    const userText = input.trim();
    setInput("");
    setError(null);

    const userMsg: OnboardingMessage = { role: "user", content: userText };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setIsSending(true);

    // Build history for the API (exclude the current user message — it's in `message`)
    const historyForApi = messages.map(m => ({ role: m.role, content: m.content }));

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          turn_number: turnNumber,
          message: userText,
          chat_history: historyForApi,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${res.status}`);
      }

      const data = await res.json();

        if (data.is_complete) {
        // Turn 5 complete — show Mission Brief then unlock dashboard
        setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
        setIsFinishing(true);
        // Store full profile_matrix so DashboardOverview can read target_role, baseline_level etc.
        if (data.profile_matrix) {
          localStorage.setItem("aimos_profile_matrix", JSON.stringify(data.profile_matrix));
        }
        // Longer pause to let the user read the Mission Brief before transitioning
        setTimeout(() => onComplete(), 3800);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
        setTurnNumber(data.turn_number + 1);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "An unexpected error occurred.";
      setError(msg);
      // Revert user message on failure
      setMessages(messages);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Progress: 5 turns total, starting at turn 1
  const progressPct = turnNumber > 0 ? Math.min(((turnNumber - 1) / 5) * 100, 100) : 0;

  return (
    <div className="onboarding-root">
      {/* Ambient background orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />

      <div className={`onboarding-panel ${isFinishing ? "panel-completing" : ""}`}>
        {/* ── Header ── */}
        <div className="onboarding-header">
          <div style={{ display: "flex", alignItems: "center", width: "100%", justifyContent: "space-between" }}>
            <div className="header-logo">
              <div className={`activity-ring ${isSending ? "ring-active" : ""}`}>
                <span className="logo-icon">⬡</span>
              </div>
              <div>
                <h1 className="header-title">AI-MOS Diagnostic</h1>
                <p className="header-subtitle">Building your personalized learning profile</p>
              </div>
            </div>

            {onOpenKeys && (
              <button
                onClick={onOpenKeys}
                className="onboarding-key-btn"
                title="Configure Compute API Keys"
                type="button"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="onboarding-key-icon">
                  <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
                </svg>
              </button>
            )}
          </div>

          {/* Progress bar */}
          <div className="progress-area">
            <span className="progress-label">
              {isFinishing
                ? "Mission Brief Finalized ✓"
                : turnNumber > 0
                ? `Diagnostic Protocol — Step ${Math.min(turnNumber, 5)} of 5`
                : "Initializing…"}
            </span>
            <div className="progress-track">
              <div
                className="progress-fill"
                style={{ width: isFinishing ? "100%" : `${progressPct}%` }}
              />
            </div>
          </div>
        </div>

        {/* ── Chat Log ── */}
        <div ref={chatLogRef} className="onboarding-chat-log">
          {isLoading ? (
            <div className="loading-state">
              <div className="loading-dots">
                <span /><span /><span />
              </div>
              <p>Connecting to diagnostic advisor…</p>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`bubble-wrapper ${msg.role === "user" ? "bubble-user-wrapper" : "bubble-assistant-wrapper"}`}
                >
                  {msg.role === "assistant" && (
                    <div className="avatar avatar-assistant">⬡</div>
                  )}
                  <div className={`bubble ${msg.role === "user" ? "bubble-user" : "bubble-assistant"}`}>
                    {msg.content}
                  </div>
                  {msg.role === "user" && (
                    <div className="avatar avatar-user">You</div>
                  )}
                </div>
              ))}

              {/* Typing indicator while waiting */}
              {isSending && (
                <div className="bubble-wrapper bubble-assistant-wrapper">
                  <div className="avatar avatar-assistant">⬡</div>
                  <div className="bubble bubble-assistant bubble-typing">
                    <span /><span /><span />
                  </div>
                </div>
              )}

              {/* Finishing card — Student Mission Brief */}
              {isFinishing && (() => {
                let profile: Record<string, string> = {};
                try {
                  const raw = localStorage.getItem("aimos_profile_matrix");
                  if (raw) profile = JSON.parse(raw);
                } catch {/* ignore */}
                return (
                  <div className="finishing-card">
                    <div className="finishing-icon">✦</div>
                    <p className="finishing-title">Student Mission Brief Generated</p>
                    <p className="finishing-sub">Your personalized OS dashboard is being prepared</p>

                    {/* Mission Brief display */}
                    {profile.target_role && (
                      <div className="mission-brief">
                        <div className="brief-row">
                          <span className="brief-label">TARGET ROLE</span>
                          <span className="brief-value">{profile.target_role}</span>
                        </div>
                        {profile.target_companies && (
                          <div className="brief-row">
                            <span className="brief-label">TARGET COMPANIES</span>
                            <span className="brief-value">{profile.target_companies}</span>
                          </div>
                        )}
                        {profile.baseline_level && (
                          <div className="brief-row">
                            <span className="brief-label">BASELINE LEVEL</span>
                            <span className="brief-value">{profile.baseline_level}</span>
                          </div>
                        )}
                        {profile.estimated_weeks && (
                          <div className="brief-row">
                            <span className="brief-label">EST. TIMELINE</span>
                            <span className="brief-value">{profile.estimated_weeks}</span>
                          </div>
                        )}
                        {profile.recommended_path && (
                          <div className="brief-row brief-row-full">
                            <span className="brief-label">RECOMMENDED PATH</span>
                            <span className="brief-value brief-path">{profile.recommended_path}</span>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="finishing-bar">
                      <div className="finishing-bar-fill" />
                    </div>
                  </div>
                );
              })()}

              {error && (
                <div className="error-banner">
                  <span>⚠</span> {error}
                </div>
              )}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        {/* ── Input Area ── */}
        {!isFinishing && (
          <div className="onboarding-input-area">
            <textarea
              ref={inputRef}
              className="onboarding-textarea"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isLoading
                  ? "Connecting…"
                  : turnNumber === 5
                  ? "Type your final answer…"
                  : "Type your response and press Enter…"
              }
              disabled={isLoading || isSending}
              rows={2}
            />
            <button
              className={`onboarding-send-btn ${isSending || isLoading ? "btn-disabled" : ""}`}
              onClick={handleSend}
              disabled={isLoading || isSending || !input.trim()}
              aria-label="Send response"
            >
              {isSending ? (
                <svg className="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              )}
            </button>
          </div>
        )}
      </div>

      <style>{`
        /* ── Root & Background ── */
        .onboarding-root {
          position: fixed; inset: 0;
          display: flex; align-items: center; justify-content: center;
          background: #020817;
          font-family: 'Inter', system-ui, sans-serif;
          overflow: hidden;
          z-index: 9999;
        }

        /* Ambient orbs */
        .orb {
          position: absolute; border-radius: 50%;
          filter: blur(80px); opacity: 0.18; pointer-events: none;
          animation: orb-drift 12s ease-in-out infinite alternate;
        }
        .orb-1 {
          width: 500px; height: 500px;
          background: radial-gradient(circle, #6366f1, #312e81);
          top: -120px; left: -100px;
          animation-delay: 0s;
        }
        .orb-2 {
          width: 400px; height: 400px;
          background: radial-gradient(circle, #0ea5e9, #0c4a6e);
          bottom: -100px; right: -80px;
          animation-delay: -6s;
        }
        @keyframes orb-drift {
          0%   { transform: translate(0, 0) scale(1); }
          100% { transform: translate(30px, 20px) scale(1.08); }
        }

        /* ── Panel ── */
        .onboarding-panel {
          position: relative; z-index: 1;
          width: min(680px, 96vw);
          height: min(680px, 85vh);
          margin: auto;
          display: flex; flex-direction: column;
          background: rgba(15, 23, 42, 0.85);
          border: 1px solid rgba(99, 102, 241, 0.25);
          border-radius: 20px;
          backdrop-filter: blur(24px);
          overflow: hidden;
          box-shadow:
            0 0 0 1px rgba(99,102,241,0.08),
            0 32px 80px rgba(0,0,0,0.6),
            0 0 60px rgba(99,102,241,0.08);
          animation: panel-in 0.5s cubic-bezier(0.16,1,0.3,1) both;
          transition: box-shadow 0.6s ease, transform 0.6s ease;
        }
        .panel-completing {
          box-shadow:
            0 0 0 1px rgba(16,185,129,0.35),
            0 32px 80px rgba(0,0,0,0.6),
            0 0 80px rgba(16,185,129,0.15);
        }
        @keyframes panel-in {
          from { opacity: 0; transform: translateY(24px) scale(0.97); }
          to   { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* ── Header ── */
        .onboarding-header {
          padding: 22px 26px 16px;
          border-bottom: 1px solid rgba(99,102,241,0.15);
          flex-shrink: 0;
        }
        .onboarding-key-btn {
          background: rgba(30, 41, 59, 0.7);
          border: 1px solid rgba(99, 102, 241, 0.25);
          color: #818cf8;
          border-radius: 10px;
          padding: 8px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
          margin-bottom: 16px;
        }
        .onboarding-key-btn:hover {
          background: rgba(99, 102, 241, 0.15);
          border-color: rgba(99, 102, 241, 0.6);
          box-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
        }
        .onboarding-key-icon {
          width: 16px;
          height: 16px;
        }
        .header-logo {
          display: flex; align-items: center; gap: 14px;
          margin-bottom: 16px;
        }
        .activity-ring {
          width: 44px; height: 44px;
          border-radius: 50%;
          border: 2px solid rgba(99,102,241,0.4);
          display: flex; align-items: center; justify-content: center;
          transition: border-color 0.3s, box-shadow 0.3s;
        }
        .ring-active {
          border-color: rgba(99,102,241,0.9);
          box-shadow: 0 0 16px rgba(99,102,241,0.4);
          animation: pulse-ring 1.2s ease-in-out infinite;
        }
        @keyframes pulse-ring {
          0%, 100% { box-shadow: 0 0 8px rgba(99,102,241,0.3); }
          50%       { box-shadow: 0 0 20px rgba(99,102,241,0.7); }
        }
        .logo-icon {
          font-size: 20px; color: #818cf8;
          animation: hex-spin 8s linear infinite;
        }
        @keyframes hex-spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        .header-title {
          font-size: 16px; font-weight: 700;
          color: #e2e8f0; margin: 0; letter-spacing: 0.01em;
        }
        .header-subtitle {
          font-size: 12px; color: #64748b; margin: 2px 0 0;
        }

        /* Progress bar */
        .progress-area { display: flex; flex-direction: column; gap: 6px; }
        .progress-label { font-size: 11px; color: #64748b; text-align: right; }
        .progress-track {
          height: 3px; background: rgba(99,102,241,0.12); border-radius: 99px; overflow: hidden;
        }
        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #6366f1, #818cf8);
          border-radius: 99px;
          transition: width 0.7s cubic-bezier(0.16,1,0.3,1);
        }

        /* ── Chat Log ── */
        .onboarding-chat-log {
          flex: 1; overflow-y: auto; padding: 20px 24px;
          display: flex; flex-direction: column; gap: 14px;
          scroll-behavior: smooth;
          min-height: 0;
        }
        .onboarding-chat-log::-webkit-scrollbar { width: 4px; }
        .onboarding-chat-log::-webkit-scrollbar-track { background: transparent; }
        .onboarding-chat-log::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 99px; }

        /* ── Bubbles ── */
        .bubble-wrapper {
          display: flex; align-items: flex-start; gap: 10px;
          animation: bubble-in 0.3s cubic-bezier(0.16,1,0.3,1) both;
        }
        @keyframes bubble-in {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .bubble-user-wrapper { flex-direction: row-reverse; }

        .avatar {
          width: 30px; height: 30px; border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          font-size: 11px; font-weight: 700; flex-shrink: 0;
          margin-top: 2px;
        }
        .avatar-assistant {
          background: rgba(99,102,241,0.15); color: #818cf8;
          border: 1px solid rgba(99,102,241,0.3);
          font-size: 14px;
        }
        .avatar-user {
          background: rgba(14,165,233,0.15); color: #38bdf8;
          border: 1px solid rgba(14,165,233,0.3);
          font-size: 9px; letter-spacing: 0.05em;
        }

        .bubble {
          max-width: 82%; padding: 12px 16px;
          border-radius: 14px; font-size: 14px; line-height: 1.6;
          white-space: pre-wrap; word-break: break-word;
        }
        .bubble-assistant {
          background: rgba(30,41,59,0.8);
          border: 1px solid rgba(99,102,241,0.15);
          color: #cbd5e1;
          border-top-left-radius: 4px;
        }
        .bubble-user {
          background: rgba(99,102,241,0.18);
          border: 1px solid rgba(99,102,241,0.3);
          color: #e2e8f0;
          border-top-right-radius: 4px;
        }

        /* Typing indicator */
        .bubble-typing {
          display: flex; align-items: center; gap: 5px; padding: 14px 18px;
        }
        .bubble-typing span {
          width: 6px; height: 6px; background: #6366f1; border-radius: 50%;
          animation: typing-bounce 1.2s ease-in-out infinite;
        }
        .bubble-typing span:nth-child(2) { animation-delay: 0.15s; }
        .bubble-typing span:nth-child(3) { animation-delay: 0.3s; }
        @keyframes typing-bounce {
          0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
          40%            { transform: translateY(-6px); opacity: 1; }
        }

        /* ── Loading state ── */
        .loading-state {
          display: flex; flex-direction: column; align-items: center;
          gap: 14px; padding: 40px 0; color: #64748b; font-size: 13px;
        }
        .loading-dots { display: flex; gap: 7px; }
        .loading-dots span {
          width: 8px; height: 8px; background: #6366f1; border-radius: 50%;
          animation: typing-bounce 1.2s ease-in-out infinite;
        }
        .loading-dots span:nth-child(2) { animation-delay: 0.15s; }
        .loading-dots span:nth-child(3) { animation-delay: 0.3s; }

        /* ── Finishing card ── */
        .finishing-card {
          display: flex; flex-direction: column; align-items: center;
          gap: 8px; padding: 28px; margin-top: 8px;
          background: rgba(16,185,129,0.07);
          border: 1px solid rgba(16,185,129,0.25);
          border-radius: 14px;
          animation: bubble-in 0.4s cubic-bezier(0.16,1,0.3,1);
        }
        .finishing-icon {
          font-size: 28px; color: #10b981;
          animation: star-pulse 1.5s ease-in-out infinite;
        }
        @keyframes star-pulse {
          0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.8; }
          50%       { transform: scale(1.15) rotate(15deg); opacity: 1; }
        }
        .finishing-title { font-size: 15px; font-weight: 600; color: #34d399; margin: 0; }
        .finishing-sub   { font-size: 12px; color: #64748b; margin: 0; }
        .finishing-bar {
          width: 100%; height: 3px; background: rgba(16,185,129,0.15);
          border-radius: 99px; overflow: hidden; margin-top: 6px;
        }
        .finishing-bar-fill {
          height: 100%; width: 0;
          background: linear-gradient(90deg, #10b981, #34d399);
          border-radius: 99px;
          animation: fill-bar 2s linear forwards;
        }
        @keyframes fill-bar {
          to { width: 100%; }
        }

        /* ── Student Mission Brief ── */
        .mission-brief {
          width: 100%; margin-top: 12px;
          border: 1px solid rgba(16,185,129,0.2);
          border-radius: 10px; overflow: hidden;
          font-size: 12px;
        }
        .brief-row {
          display: grid; grid-template-columns: 120px 1fr;
          border-bottom: 1px solid rgba(16,185,129,0.1);
        }
        .brief-row:last-child { border-bottom: none; }
        .brief-row-full { grid-template-columns: 1fr; }
        .brief-label {
          padding: 7px 10px; font-size: 9px; font-weight: 700;
          letter-spacing: 0.1em; color: #6ee7b7;
          background: rgba(16,185,129,0.07);
          text-transform: uppercase;
          border-right: 1px solid rgba(16,185,129,0.1);
          display: flex; align-items: center;
        }
        .brief-row-full .brief-label {
          border-right: none; border-bottom: 1px solid rgba(16,185,129,0.1);
        }
        .brief-value {
          padding: 7px 10px; color: #e2e8f0; font-weight: 500;
          display: flex; align-items: center;
        }
        .brief-path {
          font-size: 11px; color: #a5f3fc; font-family: monospace; word-break: break-word;
        }

        /* ── Error banner ── */
        .error-banner {
          display: flex; align-items: center; gap: 8px;
          padding: 10px 14px; border-radius: 10px;
          background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3);
          color: #fca5a5; font-size: 13px;
          animation: bubble-in 0.3s ease;
        }

        /* ── Input Area ── */
        .onboarding-input-area {
          display: flex; align-items: flex-end; gap: 10px;
          padding: 16px 20px;
          border-top: 1px solid rgba(99,102,241,0.15);
          flex-shrink: 0;
        }
        .onboarding-textarea {
          flex: 1; resize: none;
          background: rgba(15,23,42,0.6);
          border: 1px solid rgba(99,102,241,0.25);
          border-radius: 12px;
          color: #e2e8f0; font-size: 14px; line-height: 1.5;
          padding: 10px 14px;
          outline: none; font-family: inherit;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .onboarding-textarea:focus {
          border-color: rgba(99,102,241,0.6);
          box-shadow: 0 0 0 3px rgba(99,102,241,0.12);
        }
        .onboarding-textarea::placeholder { color: #475569; }
        .onboarding-textarea:disabled { opacity: 0.5; cursor: not-allowed; }

        .onboarding-send-btn {
          width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
          display: flex; align-items: center; justify-content: center;
          background: linear-gradient(135deg, #6366f1, #4f46e5);
          border: none; cursor: pointer; color: white;
          transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
          box-shadow: 0 4px 12px rgba(99,102,241,0.35);
        }
        .onboarding-send-btn svg { width: 18px; height: 18px; }
        .onboarding-send-btn:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 6px 18px rgba(99,102,241,0.5);
        }
        .onboarding-send-btn:active:not(:disabled) { transform: scale(0.95); }
        .btn-disabled, .onboarding-send-btn:disabled {
          opacity: 0.4; cursor: not-allowed; transform: none !important;
        }
        .spin-icon { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
