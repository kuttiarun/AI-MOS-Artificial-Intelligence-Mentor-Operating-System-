import React, { useState, useEffect } from "react";
import { Key, ShieldAlert, Save, RefreshCw } from "lucide-react";

interface BYOKModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BYOKModal: React.FC<BYOKModalProps> = ({ isOpen, onClose }) => {
  const [provider, setProvider] = useState("nvidia-nim");
  const [apiKey, setApiKey] = useState("");
  const [userId, setUserId] = useState("");
  const [saved, setSaved] = useState(false);

  // Load existing credentials on mount
  useEffect(() => {
    const savedProvider = localStorage.getItem("aimos_provider");
    const savedKey = localStorage.getItem("aimos_api_key");
    const savedUserId = localStorage.getItem("aimos_user_id");

    if (savedProvider) setProvider(savedProvider);
    if (savedKey) setApiKey(savedKey);
    if (savedUserId) setUserId(savedUserId);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) return;

    localStorage.setItem("aimos_provider", provider);
    localStorage.setItem("aimos_api_key", apiKey.trim());
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md transition-opacity">
      <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div className="rounded-lg bg-indigo-950 p-2 text-indigo-400">
            <Key size={20} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-100">BYOK Configuration</h2>
            <p className="text-xs text-slate-400">Bring Your Own Key credentials setup</p>
          </div>
        </div>

        {/* Security Warning Card */}
        <div className="mt-4 flex gap-3 rounded-lg border border-slate-800/80 bg-slate-950/50 p-3">
          <ShieldAlert className="shrink-0 text-amber-500" size={18} />
          <p className="text-xs text-slate-400 leading-relaxed">
            <strong className="text-slate-200">Security Notice:</strong> Your API keys are processed strictly in-memory on your local browser. Our platform servers never store, replicate, or log your credentials.
          </p>
        </div>

        <form onSubmit={handleSave} className="mt-5 space-y-4">
          {/* Provider Selection */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Select Compute Provider
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="nvidia-nim">NVIDIA NIM (meta/llama-3.1-70b)</option>
              <option value="openai">OpenAI (Phase 2 stub)</option>
              <option value="google-gemini">Google Gemini (Phase 2 stub)</option>
              <option value="anthropic">Anthropic (Phase 2 stub)</option>
            </select>
          </div>

          {/* API Key */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Developer API Key
            </label>
            <input
              type="password"
              placeholder="e.g. nvapi-xxxxxxxxxxxx"
              required
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-600"
            />
          </div>

          {/* User ID Fallback */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Student User ID (Optional UUID)
            </label>
            <input
              type="text"
              placeholder="Leave empty for default seeded dev profile"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-700"
            />
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-2 pt-2">
            {localStorage.getItem("aimos_api_key") && (
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
