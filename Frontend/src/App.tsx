import { useState, useEffect, useCallback } from "react";
import { CurriculumTree } from "./components/CurriculumTree";
import { LessonCanvas } from "./components/LessonCanvas";
import { SocraticConsole } from "./components/SocraticConsole";
import { BYOKModal } from "./components/BYOKModal";
import { OnboardingChat } from "./components/OnboardingChat";
import { DashboardOverview } from "./components/DashboardOverview";
import { LoginScreen } from "./components/LoginScreen";
import { InterviewPanel } from "./components/InterviewPanel";
import { useLlmStream } from "./hooks/useLlmStream";
import type { Message } from "./hooks/useLlmStream";
import type { NodeItem } from "./components/CurriculumTree";

// ─── Onboarding Gate Status ───────────────────────────────────────────────────
// null  = checking status (loading)
// false = onboarding needed (show diagnostic)
// true  = onboarding done  (show dashboard)
type OnboardingStatus = boolean | null;

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("aimos_user_id"));
  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatus>(null);
  const [dashboardVisible, setDashboardVisible] = useState(false);

  // ── View state: "dashboard" | "lesson" | "interview" ─────────────────────────
  const [activeView, setActiveView] = useState<"dashboard" | "lesson" | "interview">("dashboard");
  const [activeNodeId, setActiveNodeId] = useState("java-collections-hashmap");

  // ── Shared curriculum nodes state (lifted up from CurriculumTree) ───────────
  const [nodes, setNodes] = useState<NodeItem[]>([]);
  const [isLoadingNodes, setIsLoadingNodes] = useState(true);

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "mentor",
      content: "Hello! I am your Socratic Mentor. Let's explore the concepts in this lesson together. What questions or thoughts do you have?",
    },
  ]);
  const [isKeysOpen, setIsKeysOpen] = useState(false);

  const { streamChat, isStreaming, error, setError } = useLlmStream();

  // ── Derived: weak area count for Context Inspector ─────────────────────────
  const weakAreaCount = nodes.filter(
    n => n.status === "in_progress" || n.status === "unlocked"
  ).length;

  // ── Fetch curriculum nodes (lifted from CurriculumTree so Dashboard can share it) ──
  const fetchNodes = useCallback(async () => {
    setIsLoadingNodes(true);
    const userId = localStorage.getItem("aimos_user_id");
    try {
      const response = await fetch("http://localhost:8000/api/v1/curriculum/progress", {
        headers: { ...(userId ? { "X-User-Id": userId } : {}) },
      });
      if (response.ok) {
        const data: NodeItem[] = await response.json();
        setNodes(data);
      }
    } catch {
      // Backend unreachable — keep empty, CurriculumTree uses its own fallback
    } finally {
      setIsLoadingNodes(false);
    }
  }, []);

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
    if (!isLoggedIn) {
      // If not logged in, reset status to bypass loading spinners
      setOnboardingStatus(false);
      return;
    }
    const userId = localStorage.getItem("aimos_user_id");

    fetch("http://localhost:8000/api/v1/onboarding/status", {
      headers: {
        ...(userId ? { "X-User-Id": userId } : {}),
      },
    })
      .then(r => r.json())
      .then((data: { onboarding_complete: boolean }) => {
        setOnboardingStatus(data.onboarding_complete);
        if (data.onboarding_complete) {
          setTimeout(() => setDashboardVisible(true), 80);
          fetchNodes();
        }
      })
      .catch(() => {
        // Fail open: backend unreachable — show dashboard directly
        setOnboardingStatus(true);
        setTimeout(() => setDashboardVisible(true), 80);
        fetchNodes();
      });
  }, [fetchNodes, isLoggedIn]);

  // ── 3. Initialize chat log with welcome prompt on node changes ────────────
  useEffect(() => {
    setMessages([
      {
        role: "mentor",
        content:
          "Hello! I am your Socratic Mentor. Let's explore the concepts in this lesson together. What questions or thoughts do you have?",
      },
    ]);
    setError(null);
  }, [activeNodeId, setError]);

  // ── 4. Re-fetch nodes after node changes (validation may have unlocked new nodes) ──
  useEffect(() => {
    if (onboardingStatus) fetchNodes();
  }, [activeNodeId, onboardingStatus, fetchNodes]);

  // ── 5. Handle sending chat message to BYOK streaming gateway ──────────────
  const handleSendMessage = async (text: string) => {
    const userMsg: Message = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);

    let mentorResponse = "";
    await streamChat(
      text,
      activeNodeId,
      chunk => {
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
    fetchNodes();
    if (activeNodeId === "java-collections-hashmap") {
      alert("🎉 Congratulations! You have completed the HashMap internals syllabus. Check back for upcoming lessons!");
    } else {
      setActiveNodeId("java-collections-hashmap");
    }
  };

  // ── 6. Handle node selection — always switch to lesson view ───────────────
  const handleSelectNode = (id: string) => {
    setActiveNodeId(id);
    setActiveView("lesson");
  };

  // ── 7. Handle going home to OS dashboard ──────────────────────────────────
  const handleGoHome = () => {
    setActiveView("dashboard");
  };

  // ── 8. Onboarding completion handler ──────────────────────────────────────
  const handleOnboardingComplete = () => {
    setOnboardingStatus(true);
    fetchNodes();
    // Small delay so the OnboardingChat finishing animation plays first
    setTimeout(() => setDashboardVisible(true), 400);
  };

  // ── 9. Login success handler ──────────────────────────────────────────────
  const handleLoginSuccess = (userId: string, email: string, onboardingComplete: boolean) => {
    setIsLoggedIn(true);
    setOnboardingStatus(onboardingComplete);
    if (onboardingComplete) {
      setTimeout(() => setDashboardVisible(true), 80);
      fetchNodes();
    }
  };

  // ── Render: Login Page ─────────────────────────────────────────────────────
  if (!isLoggedIn) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  // ── Render: Loading state ──────────────────────────────────────────────────
  if (onboardingStatus === null) {
    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "#020817",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={{ textAlign: "center", color: "#475569", fontFamily: "system-ui" }}>
          <div
            style={{
              width: 36,
              height: 36,
              margin: "0 auto 16px",
              border: "3px solid rgba(99,102,241,0.3)",
              borderTopColor: "#6366f1",
              borderRadius: "50%",
              animation: "spin 0.9s linear infinite",
            }}
          />
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
        <OnboardingChat onComplete={handleOnboardingComplete} onOpenKeys={() => setIsKeysOpen(true)} />
        <BYOKModal isOpen={isKeysOpen} onClose={() => setIsKeysOpen(false)} />
      </>
    );
  }

  // ── Render: Main workspace ─────────────────────────────────────────────────
  return (
    <div
      className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans"
      style={{
        opacity: dashboardVisible ? 1 : 0,
        transform: dashboardVisible ? "none" : "scale(0.98)",
        transition: "opacity 0.5s ease, transform 0.5s ease",
      }}
    >
      {/* Column 1: Curriculum tree navigation (15% width) */}
      <aside className="w-[15%] min-w-[180px] h-full shrink-0">
        <CurriculumTree
          activeNodeId={activeNodeId}
          onSelectNode={handleSelectNode}
          onGoHome={handleGoHome}
          isDashboardActive={activeView === "dashboard"}
        />
      </aside>

      {/* Column 2: Center canvas — OS Dashboard | Lesson Content | Interview Panel */}
      <main className="w-[50%] flex-1 h-full border-r border-slate-800">
        {activeView === "dashboard" ? (
          <DashboardOverview
            nodes={nodes}
            onSelectNode={handleSelectNode}
            isLoadingNodes={isLoadingNodes}
            onEnterInterview={() => setActiveView("interview")}
          />
        ) : activeView === "interview" ? (
          <InterviewPanel onGoBack={() => setActiveView("dashboard")} />
        ) : (
          <LessonCanvas activeNodeId={activeNodeId} onAdvanceNode={handleAdvanceNode} />
        )}
      </main>

      {/* Column 3: Socratic Compute Hub (35% width) */}
      <section className="w-[35%] min-w-[320px] h-full shrink-0">
        <SocraticConsole
          messages={messages}
          isStreaming={isStreaming}
          error={error}
          onSendMessage={handleSendMessage}
          onOpenKeys={() => setIsKeysOpen(true)}
          activeNodeId={activeView === "dashboard" ? "os-dashboard" : activeNodeId}
          weakAreaCount={weakAreaCount}
        />
      </section>

      {/* Credentials overlay */}
      <BYOKModal isOpen={isKeysOpen} onClose={() => setIsKeysOpen(false)} />
    </div>
  );
}

export default App;
