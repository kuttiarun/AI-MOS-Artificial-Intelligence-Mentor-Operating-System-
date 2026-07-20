import React, { useState } from "react";
import { Brain, Key, LogIn, Mail, Lock, Sparkles, UserCheck } from "lucide-react";

interface LoginScreenProps {
  onLoginSuccess: (userId: string, email: string, onboardingComplete: boolean) => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showGooglePicker, setShowGooglePicker] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState("");
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Simulated Google accounts for out-of-the-box development convenience
  const mockGoogleAccounts = [
    { email: "arun@gmail.com", name: "Arun Kumar", picture: "A" },
    { email: "zoho.candidate@gmail.com", name: "Zoho Candidate", picture: "Z" },
    { email: "guest.developer@aimos.dev", name: "Guest Developer", picture: "G" }
  ];

  const handleGoogleSignIn = async (selectedEmail: string) => {
    setIsAuthenticating(true);
    setErrorMessage(null);
    setShowGooglePicker(false);

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: selectedEmail, name: "Google User" }),
      });

      if (!response.ok) {
        throw new Error("Failed to authenticate with backend Google Auth gateway.");
      }

      const data = await response.json();
      localStorage.setItem("aimos_user_id", data.user_id);
      localStorage.setItem("aimos_user_email", data.email);
      
      // Let parent component proceed
      onLoginSuccess(data.user_id, data.email, data.onboarding_complete);
    } catch (err: any) {
      setErrorMessage(err.message || "An authentication error occurred.");
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleCustomGoogleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customGoogleEmail.trim()) {
      handleGoogleSignIn(customGoogleEmail.trim());
    }
  };

  const handleRegularLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setErrorMessage("Please enter both email and password.");
      return;
    }
    
    // For out-of-the-box ease in local dev environment, regular login acts as a direct sign-in 
    // to keep onboarding flow functional
    handleGoogleSignIn(email.trim());
  };

  return (
    <div className="login-root">
      {/* Drifting glow backdrops */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />

      <div className="login-card">
        {/* Header Icon */}
        <div className="login-logo-area">
          <div className="login-ring">
            <Brain className="login-brain-icon" size={24} />
          </div>
          <h1 className="login-title">AI-MOS v2.0</h1>
          <p className="login-subtitle">Artificial Intelligence Mentor Operating System</p>
        </div>

        {errorMessage && (
          <div className="login-error">
            <span>⚠</span> {errorMessage}
          </div>
        )}

        {/* Regular Login Form */}
        <form onSubmit={handleRegularLogin} className="login-form">
          <div className="input-group">
            <label>Student Email</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={14} />
              <input
                type="email"
                placeholder="e.g. arun@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isAuthenticating}
              />
            </div>
          </div>

          <div className="input-group">
            <label>Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={14} />
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isAuthenticating}
              />
            </div>
          </div>

          <button type="submit" disabled={isAuthenticating} className="login-btn-primary">
            {isAuthenticating ? (
              <span className="flex items-center justify-center gap-2">
                <span className="login-spinner" /> Authenticating...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <LogIn size={14} /> Sign In
              </span>
            )}
          </button>
        </form>

        <div className="divider">
          <span>or continue with</span>
        </div>

        {/* Google Sign In Button */}
        <button
          type="button"
          onClick={() => setShowGooglePicker(true)}
          disabled={isAuthenticating}
          className="google-sign-in-btn"
        >
          <svg className="google-svg" viewBox="0 0 24 24" width="16" height="16">
            <path
              fill="#EA4335"
              d="M12 5.04c1.66 0 3.2.57 4.38 1.69l3.27-3.27C17.67 1.54 14.98 1 12 1 7.35 1 3.37 3.67 1.39 7.56l3.89 3.02c1.02-3.04 3.86-5.54 6.72-5.54z"
            />
            <path
              fill="#4285F4"
              d="M23.49 12.27c0-.81-.07-1.59-.2-2.36H12v4.51h6.46c-.29 1.48-1.14 2.73-2.4 3.58l3.73 2.89c2.18-2.01 3.7-4.99 3.7-8.62z"
            />
            <path
              fill="#FBBC05"
              d="M5.28 14.42c-.25-.76-.39-1.57-.39-2.42 0-.85.14-1.66.39-2.42L1.39 6.56C.5 8.34 0 10.32 0 12c0 1.68.5 3.66 1.39 5.44l3.89-3.02z"
            />
            <path
              fill="#34A853"
              d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.73-2.89c-1.1.74-2.5 1.18-4.23 1.18-3.08 0-5.7-2.08-6.63-4.88L1.47 16.5c1.98 3.89 5.96 6.5 10.53 6.5z"
            />
          </svg>
          <span>Sign in with Google</span>
        </button>

        {/* Quick Developer Guest Sign-In */}
        <button
          type="button"
          onClick={() => handleGoogleSignIn("dev.candidate@aimos.dev")}
          disabled={isAuthenticating}
          className="login-btn-guest"
        >
          <UserCheck size={13} />
          <span>Quick Guest Dev Access</span>
        </button>
      </div>

      {/* Google Account Picker Modal */}
      {showGooglePicker && (
        <div className="picker-overlay">
          <div className="picker-modal">
            <div className="picker-header">
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg"
                alt="Google"
                className="picker-google-logo"
              />
              <h3>Sign in with Google</h3>
              <p>to continue to AI-MOS Operating System</p>
            </div>

            <div className="picker-list">
              {mockGoogleAccounts.map((acc) => (
                <button
                  key={acc.email}
                  onClick={() => handleGoogleSignIn(acc.email)}
                  className="picker-item"
                >
                  <div className="picker-avatar">{acc.picture}</div>
                  <div className="picker-info">
                    <span className="picker-name">{acc.name}</span>
                    <span className="picker-email">{acc.email}</span>
                  </div>
                </button>
              ))}
            </div>

            {/* Custom Google Email input */}
            <form onSubmit={handleCustomGoogleSubmit} className="picker-custom-form">
              <div className="divider">
                <span>or use a custom email</span>
              </div>
              <div className="custom-input-wrapper">
                <input
                  type="email"
                  placeholder="Enter your google account email"
                  value={customGoogleEmail}
                  onChange={(e) => setCustomGoogleEmail(e.target.value)}
                  required
                />
                <button type="submit">Continue</button>
              </div>
            </form>

            <button
              onClick={() => setShowGooglePicker(false)}
              className="picker-close-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <style>{`
        .login-root {
          position: fixed; inset: 0;
          display: flex; align-items: center; justify-content: center;
          background: #020817;
          font-family: 'Inter', system-ui, sans-serif;
          overflow: hidden;
          z-index: 9999;
        }
        .orb {
          position: absolute; border-radius: 50%;
          filter: blur(85px); opacity: 0.18; pointer-events: none;
          animation: drift 15s ease-in-out infinite alternate;
        }
        .orb-1 {
          width: 500px; height: 500px;
          background: radial-gradient(circle, #6366f1, #312e81);
          top: -120px; left: -100px;
        }
        .orb-2 {
          width: 450px; height: 450px;
          background: radial-gradient(circle, #8b5cf6, #4c1d95);
          bottom: -120px; right: -80px;
        }
        @keyframes drift {
          from { transform: translate(0, 0) scale(1); }
          to   { transform: translate(40px, 30px) scale(1.06); }
        }

        .login-card {
          width: min(400px, 92vw);
          padding: 30px;
          background: rgba(15, 23, 42, 0.8);
          border: 1px solid rgba(99, 102, 241, 0.25);
          border-radius: 20px;
          backdrop-filter: blur(20px);
          box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 40px rgba(99,102,241,0.06);
          display: flex; flex-direction: column; gap: 20px;
        }

        .login-logo-area {
          text-align: center;
          display: flex; flex-direction: column; align-items: center; gap: 8px;
        }
        .login-ring {
          width: 48px; height: 48px;
          border-radius: 12px;
          background: rgba(99, 102, 241, 0.15);
          border: 1px solid rgba(99, 102, 241, 0.35);
          display: flex; align-items: center; justify-content: center;
          color: #818cf8;
          box-shadow: 0 0 15px rgba(99,102,241,0.25);
        }
        .login-title {
          font-size: 18px; font-weight: 800; color: #e2e8f0; margin: 0; letter-spacing: 0.02em;
        }
        .login-subtitle {
          font-size: 11px; color: #64748b; margin: 0;
        }

        .login-error {
          padding: 8px 12px; border-radius: 8px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.25);
          color: #fca5a5; font-size: 11px;
          display: flex; align-items: center; gap: 6px;
        }

        .login-form {
          display: flex; flex-direction: column; gap: 14px;
        }
        .input-group {
          display: flex; flex-direction: column; gap: 5px;
        }
        .input-group label {
          font-size: 10px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;
        }
        .input-wrapper {
          position: relative;
          display: flex; align-items: center;
        }
        .input-icon {
          position: absolute; left: 12px; color: #475569;
        }
        .input-wrapper input {
          width: 100%;
          background: rgba(2, 6, 23, 0.6);
          border: 1px solid rgba(99, 102, 241, 0.15);
          border-radius: 10px;
          padding: 8px 12px 8px 34px;
          color: #f1f5f9; font-size: 12px;
          outline: none;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .input-wrapper input:focus {
          border-color: rgba(99, 102, 241, 0.5);
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .login-btn-primary {
          background: linear-gradient(135deg, #6366f1, #4f46e5);
          color: white; border: none;
          padding: 9px; border-radius: 10px;
          font-size: 12px; font-weight: 700;
          cursor: pointer;
          transition: transform 0.15s, box-shadow 0.15s;
          box-shadow: 0 4px 14px rgba(99,102,241,0.3);
        }
        .login-btn-primary:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(99,102,241,0.45);
        }
        .login-btn-primary:active { transform: scale(0.98); }

        .divider {
          display: flex; align-items: center; text-align: center; color: #334155; font-size: 10px;
        }
        .divider::before, .divider::after {
          content: ''; flex: 1; border-bottom: 1px solid #1e293b;
        }
        .divider span { padding: 0 10px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; }

        .google-sign-in-btn {
          background: #ffffff; color: #1e293b;
          border: 1px solid #cbd5e1;
          padding: 9px; border-radius: 10px;
          font-size: 12px; font-weight: 700;
          cursor: pointer;
          display: flex; align-items: center; justify-content: center; gap: 8px;
          transition: background-color 0.2s, box-shadow 0.2s, transform 0.15s;
        }
        .google-sign-in-btn:hover {
          background: #f8fafc;
          box-shadow: 0 4px 12px rgba(255,255,255,0.1);
          transform: translateY(-0.5px);
        }
        .google-sign-in-btn:active { transform: scale(0.98); }

        .login-btn-guest {
          background: transparent; color: #818cf8;
          border: 1px solid rgba(99, 102, 241, 0.2);
          padding: 8px; border-radius: 10px;
          font-size: 11px; font-weight: 600;
          cursor: pointer;
          display: flex; align-items: center; justify-content: center; gap: 6px;
          transition: background-color 0.2s, border-color 0.2s;
        }
        .login-btn-guest:hover {
          background: rgba(99, 102, 241, 0.08);
          border-color: rgba(99, 102, 241, 0.4);
        }

        /* ── Account Picker Modal ── */
        .picker-overlay {
          position: fixed; inset: 0; z-index: 10000;
          background: rgba(2, 6, 23, 0.8);
          backdrop-filter: blur(8px);
          display: flex; align-items: center; justify-content: center;
        }
        .picker-modal {
          width: min(360px, 92vw);
          background: #0f172a;
          border: 1px solid #1e293b;
          border-radius: 16px;
          padding: 24px;
          display: flex; flex-direction: column; gap: 16px;
          box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        .picker-header {
          text-align: center;
          display: flex; flex-direction: column; align-items: center; gap: 4px;
        }
        .picker-google-logo { height: 20px; margin-bottom: 8px; }
        .picker-header h3 { font-size: 15px; font-weight: 700; color: #e2e8f0; margin: 0; }
        .picker-header p { font-size: 11px; color: #64748b; margin: 0; }

        .picker-list {
          display: flex; flex-direction: column; gap: 8px;
        }
        .picker-item {
          display: flex; align-items: center; gap: 12px;
          padding: 10px 14px; border-radius: 10px;
          background: rgba(30, 41, 59, 0.4);
          border: 1px solid rgba(255,255,255,0.02);
          text-align: left; cursor: pointer;
          transition: background-color 0.15s, border-color 0.15s;
        }
        .picker-item:hover {
          background: rgba(99, 102, 241, 0.08);
          border-color: rgba(99, 102, 241, 0.2);
        }
        .picker-avatar {
          width: 32px; height: 32px; border-radius: 50%;
          background: #4f46e5; color: white;
          display: flex; align-items: center; justify-content: center;
          font-size: 12px; font-weight: 700;
        }
        .picker-info { display: flex; flex-direction: column; }
        .picker-name { font-size: 12px; font-weight: 600; color: #f1f5f9; }
        .picker-email { font-size: 10px; color: #64748b; }

        .picker-custom-form {
          display: flex; flex-direction: column; gap: 8px;
        }
        .custom-input-wrapper {
          display: flex; gap: 6px;
        }
        .custom-input-wrapper input {
          flex: 1; background: #020617; border: 1px solid #1e293b;
          border-radius: 8px; padding: 6px 10px; color: #f1f5f9; font-size: 11px;
          outline: none;
        }
        .custom-input-wrapper input:focus { border-color: #6366f1; }
        .custom-input-wrapper button {
          background: #6366f1; color: white; border: none; padding: 6px 12px;
          border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer;
        }

        .picker-close-btn {
          background: transparent; border: none; color: #64748b; font-size: 11px;
          cursor: pointer; padding: 4px; text-align: center;
        }
        .picker-close-btn:hover { color: #cbd5e1; }

        .login-spinner {
          display: inline-block; width: 12px; height: 12px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: white; border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};
