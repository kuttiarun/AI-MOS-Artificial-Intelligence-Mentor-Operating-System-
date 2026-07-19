import { useState, useEffect } from "react";
import { CurriculumTree } from "./components/CurriculumTree";
import { LessonCanvas } from "./components/LessonCanvas";
import { SocraticConsole } from "./components/SocraticConsole";
import { BYOKModal } from "./components/BYOKModal";
import { useLlmStream, Message } from "./hooks/useLlmStream";

function App() {
  const [activeNodeId, setActiveNodeId] = useState("java-collections-hashmap");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isKeysOpen, setIsKeysOpen] = useState(false);

  const { streamChat, isStreaming, error, setError } = useLlmStream();

  // 1. Check for API keys on initial load
  useEffect(() => {
    const hasKey = localStorage.getItem("aimos_api_key");
    const hasProvider = localStorage.getItem("aimos_provider");

    if (!hasKey || !hasProvider) {
      // Auto-open modal if keys are missing
      setIsKeysOpen(true);
    }
  }, []);

  // 2. Clear chat log on active node changes to focus context
  useEffect(() => {
    setMessages([]);
    setError(null);
  }, [activeNodeId, setError]);

  // 3. Handle sending chat message to BYOK streaming gateway
  const handleSendMessage = async (text: string) => {
    // Append the user's message
    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    // Initial placeholder for the streaming mentor response
    let mentorResponse = "";
    
    await streamChat(
      text,
      activeNodeId,
      // onChunk: appends characters as they arrive
      (chunk) => {
        mentorResponse += chunk;
        setMessages((prev) => {
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
      // onStart: hooks up any initial logs
      () => {
        // Option to log session indicators
      }
    );
  };

  const handleAdvanceNode = () => {
    // Advanced nodes checklist transitions to next unlock
    if (activeNodeId === "java-collections-hashmap") {
      alert("🎉 Congratulations! You have completed the HashMap internals syllabus. Check back for upcoming lessons!");
    } else {
      setActiveNodeId("java-collections-hashmap");
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* 3-Column Layout Workspace Setup (UI&UX.md §1) */}
      
      {/* Column 1: Curriculum tree navigation (15% width) */}
      <aside className="w-[15%] min-w-[180px] h-full shrink-0">
        <CurriculumTree
          activeNodeId={activeNodeId}
          onSelectNode={setActiveNodeId}
        />
      </aside>

      {/* Column 2: Center Lesson Canvas content (50% width) */}
      <main className="w-[50%] flex-1 h-full border-r border-slate-800">
        <LessonCanvas
          activeNodeId={activeNodeId}
          onAdvanceNode={handleAdvanceNode}
        />
      </main>

      {/* Column 3: Socratic Chat Console (35% width) */}
      <section className="w-[35%] min-w-[320px] h-full shrink-0">
        <SocraticConsole
          messages={messages}
          isStreaming={isStreaming}
          error={error}
          onSendMessage={handleSendMessage}
          onOpenKeys={() => setIsKeysOpen(true)}
        />
      </section>

      {/* Credentials overlay (PRD MOD-01) */}
      <BYOKModal
        isOpen={isKeysOpen}
        onClose={() => setIsKeysOpen(false)}
      />
    </div>
  );
}

export default App;
