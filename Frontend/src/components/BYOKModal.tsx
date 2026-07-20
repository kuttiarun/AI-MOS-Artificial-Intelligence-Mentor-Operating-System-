import React, { useState, useEffect } from "react";
import { Key, ShieldAlert, Save, RefreshCw } from "lucide-react";

interface BYOKModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BYOKModal: React.FC<BYOKModalProps> = ({ isOpen, onClose }) => {
  const [provider, setProvider] = useState("nvidia-nim");
  const [nvidiaKey, setNvidiaKey] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [geminiKey, setGeminiKey] = useState("");
  const [anthropicKey, setAnthropicKey] = useState("");
  const [userId, setUserId] = useState("");
  const [saved, setSaved] = useState(false);

  // Load existing credentials on mount
  useEffect(() => {
    const savedProvider = localStorage.getItem("aimos_provider") || "nvidia-nim";
    const savedNvidia = localStorage.getItem("aimos_nvidia_api_key") || "";
    const savedOpenai = localStorage.getItem("aimos_openai_api_key") || "";
    const savedGemini = localStorage.getItem("aimos_gemini_api_key") || "";
    const savedAnthropic = localStorage.getItem("aimos_anthropic_api_key") || "";
    const savedUserId = localStorage.getItem("aimos_user_id") || "";

    setProvider(savedProvider);
    setNvidiaKey(savedNvidia);
    setOpenaiKey(savedOpenai);
    setGeminiKey(savedGemini);
    setAnthropicKey(savedAnthropic);
    setUserId(savedUserId);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();

    // 1. Save specific keys
    localStorage.setItem("aimos_provider", provider);
    localStorage.setItem("aimos_nvidia_api_key", nvidiaKey.trim());
    localStorage.setItem("aimos_openai_api_key", openaiKey.trim());
    localStorage.setItem("aimos_gemini_api_key", geminiKey.trim());
    localStorage.setItem("aimos_anthropic_api_key", anthropicKey.trim());

    // 2. Sync backward compatible active key helper matching current provider
    let activeKey = "";
    if (provider === "nvidia-nim") activeKey = nvidiaKey.trim();
    if (provider === "openai") activeKey = openaiKey.trim();
    if (provider === "google-gemini") activeKey = geminiKey.trim();
    if (provider === "anthropic") activeKey = anthropicKey.trim();
    
    localStorage.setItem("aimos_api_key", activeKey);

    // 3. User ID sync
    if (userId.trim()) {
      localStorage.setItem("aimos_user_id", userId.trim());
    } else {
      localStorage.removeItem("aimos_user_id");
    }

    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 800);
  };

  const hasAnyKey = () => {
    return !!(
      localStorage.getItem("aimos_nvidia_api_key") ||
      localStorage.getItem("aimos_openai_api_key") ||
      localStorage.getItem("aimos_gemini_api_key") ||
      localStorage.getItem("aimos_anthropic_api_key")
    );
  };

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-slate-950/80 backdrop-blur-md transition-opacity">
      <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div className="rounded-lg bg-indigo-950 p-2 text-indigo-400">
            <Key size={20} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-100">BYOK Configuration</h2>
            <p className="text-xs text-slate-400">Multi-Model Developer Key Hub</p>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-3 flex gap-3 rounded-lg border border-slate-800/80 bg-slate-950/50 p-3">
          <ShieldAlert className="shrink-0 text-amber-500" size={18} />
          <p className="text-[11px] text-slate-400 leading-relaxed">
            <strong className="text-slate-200">Security Notice:</strong> Your keys are stored strictly inside your local browser. Our platform servers never log, view, or store them.
          </p>
        </div>

        <form onSubmit={handleSave} className="mt-4 space-y-3.5">
          {/* Provider Dropdown */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">
              Active LLM Compute Provider
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="nvidia-nim">NVIDIA NIM (meta/llama-3.1-70b)</option>
              <option value="openai">OpenAI (GPT-4o mini)</option>
              <option value="google-gemini">Google AI Studio (Gemini 2.5 Flash)</option>
              <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
            </select>
          </div>

          {/* Key 1: Nvidia */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-0.5">
              NVIDIA NIM API Key
            </label>
            <input
              type="password"
              placeholder="e.g. nvapi-xxxxxxxxxxxx"
              value={nvidiaKey}
              onChange={(e) => setNvidiaKey(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-700"
            />
          </div>

          {/* Key 2: OpenAI */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-0.5">
              OpenAI API Key
            </label>
            <input
              type="password"
              placeholder="e.g. sk-proj-xxxxxxxxxxxx"
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-700"
            />
          </div>

          {/* Key 3: Gemini */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-0.5">
              Google Gemini API Key
            </label>
            <input
              type="password"
              placeholder="e.g. AIzaSyxxxxxxxxxxxx"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-700"
            />
          </div>

          {/* Key 4: Anthropic */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-0.5">
              Anthropic Claude API Key
            </label>
            <input
              type="password"
              placeholder="e.g. sk-ant-xxxxxxxxxxxx"
              value={anthropicKey}
              onChange={(e) => setAnthropicKey(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-700"
            />
          </div>

          {/* Student User ID */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-0.5">
              Student User ID (Optional UUID)
            </label>
            <input
              type="text"
              placeholder="Leave empty for default seeded dev profile"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-700"
            />
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800/60">
            {hasAnyKey() && (
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg border border-slate-800 px-4 py-2 text-xs text-slate-400 hover:bg-slate-950 transition-colors"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={saved}
              className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2 text-xs font-medium text-white hover:bg-indigo-500 disabled:bg-emerald-600 transition-all shadow-md shadow-indigo-950/50"
            >
              {saved ? (
                <>
                  <RefreshCw className="animate-spin" size={14} />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={14} />
                  Save Keys
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
