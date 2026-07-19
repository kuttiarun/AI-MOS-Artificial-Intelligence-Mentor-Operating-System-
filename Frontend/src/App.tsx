import { useState, useEffect } from "react";
import { CurriculumTree } from "./components/CurriculumTree";
import { LessonCanvas } from "./components/LessonCanvas";
import { SocraticConsole } from "./components/SocraticConsole";
import { BYOKModal } from "./components/BYOKModal";
import { OnboardingChat } from "./components/OnboardingChat";
import { useLlmStream } from "./hooks/useLlmStream";
import type { Message } from "./hooks/useLlmStream";

// ─── Onboarding Gate Status ───────────────────────────────────────────────────
// null  = checking status (loading)
// false = onboarding needed (show diagnostic)
// true  = onboarding done  (show dashboard)
type OnboardingStatus = boolean | null;

function App() {
  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatus>(null);
  const [dashboardVisible, setDashboardVisible] = useState(false);
  const [activeNodeId, setActiveNodeId] = useState("java-collections-hashmap");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isKeysOpen, setIsKeysOpen] = useState(false);

  const { streamChat, isStreaming, error, setError } = useLlmStream();

  // ── 1. Check API keys on initial load ──────────────────────────────────────
  useEffect(() => {
    const hasKey = localStorage.getItem("aimos_api_key");
    const hasProvider = localStorage.getItem("aimos_provider");
    if (!hasKey || !hasProvider) {
      setIsKeysOpen(true);
    }
  }, []);

  // ── 2. Check onboarding completion status ──────────────────────────────────
  useEffect(() => {
    const userId = localStorage.getItem("aimos_user_id");

    fetch("http://localhost:8000/api/v1/onboarding/status", {
      headers: {
        ...(userId ? { "X-User-Id": userId } : {}),
      },
    })
      .then(r => r.json())
      .then((data: { onboarding_complete: boolean }) => {
        setOnboardingStatus(data.onboarding_complete);
        // If already done, fade in dashboard immediately
        if (data.onboarding_complete) {
          setTimeout(() => setDashboardVisible(true), 80);
        }
      })
      .catch(() => {
        // Fail open: backend unreachable — show dashboard directly
        setOnboardingStatus(true);
        setTimeout(() => setDashboardVisible(true), 80);
      });
  }, []);

  // ── 3. Clear chat log on active node changes ───────────────────────────────
  useEffect(() => {
    setMessages([]);
    setError(null);
  }, [activeNodeId, setError]);

  // ── 4. Handle sending chat message to BYOK streaming gateway ──────────────
  const handleSendMessage = async (text: string) => {
    const userMsg: Message = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);

    let mentorResponse = "";
    await streamChat(
      text,
      activeNodeId,
      (chunk) => {
        mentorResponse += chunk;
        setMessages(prev => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          if (updated[lastIndex] && updated[lastIndex].role === "mentor") {
            updated[lastIndex] = { role: "mentor", content: mentorResponse };
          } else {
            updated.push({ role: "mentor", content: mentorResponse });
          }
          return updated;
        });
      },
      () => {},
    );
  };

  const handleAdvanceNode = () => {
    if (activeNodeId === "java-collections-hashmap") {
      alert("🎉 Congratulations! You have completed the HashMap internals syllabus. Check back for upcoming lessons!");
    } else {
      setActiveNodeId("java-collections-hashmap");
    }
  };

  // ── 5. Onboarding completion handler ──────────────────────────────────────
  const handleOnboardingComplete = () => {
    setOnboardingStatus(true);
    // Small delay so the OnboardingChat finishing animation plays first
    setTimeout(() => setDashboardVisible(true), 400);
  };

  // ── Render: Loading state ──────────────────────────────────────────────────
  if (onboardingStatus === null) {
    return (
      <div style={{
        position: "fixed", inset: 0,
        background: "#020817",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <div style={{ textAlign: "center", color: "#475569", fontFamily: "system-ui" }}>
          <div style={{
            width: 36, height: 36, margin: "0 auto 16px",
            border: "3px solid rgba(99,102,241,0.3)",
            borderTopColor: "#6366f1",
            borderRadius: "50%",
            animation: "spin 0.9s linear infinite",
          }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <p style={{ fontSize: 13 }}>Connecting to AI-MOS…</p>
        </div>
      </div>
    );
  }

  // ── Render: Onboarding gate ────────────────────────────────────────────────
  if (!onboardingStatus) {
    return (
      <>
        <OnboardingChat onComplete={handleOnboardingComplete} />
        <BYOKModal isOpen={isKeysOpen} onClose={() => setIsKeysOpen(false)} />
      </>
    );
  }

  // ── Render: Main dashboard ─────────────────────────────────────────────────
  return (
    <div
      className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans"
      style={{
        opacity: dashboardVisible ? 1 : 0,
        transform: dashboardVisible ? "none" : "scale(0.98)",
        transition: "opacity 0.5s ease, transform 0.5s ease",
      }}
    >
      {/* 3-Column Layout Workspace */}

      {/* Column 1: Curriculum tree navigation (15% width) */}
      <aside className="w-[15%] min-w-[180px] h-full shrink-0">
        <CurriculumTree activeNodeId={activeNodeId} onSelectNode={setActiveNodeId} />
      </aside>

      {/* Column 2: Center Lesson Canvas content (50% width) */}
      <main className="w-[50%] flex-1 h-full border-r border-slate-800">
        <LessonCanvas activeNodeId={activeNodeId} onAdvanceNode={handleAdvanceNode} />
      </main>

      {/* Column 3: Socratic Chat Console (35% width) */}
      <section className="w-[35%] min-w-[320px] h-full shrink-0">
        <SocraticConsole
          messages={messages}
          isStreaming={isStreaming}
          error={error}
          onSendMessage={handleSendMessage}
          onOpenKeys={() => setIsKeysOpen(true)}
          activeNodeId={activeNodeId}
        />
      </section>

      {/* Credentials overlay */}
      <BYOKModal isOpen={isKeysOpen} onClose={() => setIsKeysOpen(false)} />
    </div>
  );
}

export default App;
