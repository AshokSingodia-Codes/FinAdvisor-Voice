import React, { useState, useEffect } from 'react';
import {
  X,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
  TrendingUp,
  Sparkles,
  RefreshCw,
  Lock,
  Mail,
  KeyRound,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../config';
import heroImage from '../assets/hero-bg.png';

type PageView = 'login' | 'signup' | 'forgot';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'signin' | 'register' | 'forgot';
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, initialTab = 'signin' }) => {
  const { login } = useAuth();

  const [view, setView] = useState<PageView>(
    initialTab === 'register' ? 'signup' : initialTab === 'forgot' ? 'forgot' : 'login'
  );

  const [signupStep, setSignupStep] = useState<1 | 2>(1);
  const [forgotStep, setForgotStep] = useState<1 | 2 | 3>(1);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [verificationToken, setVerificationToken] = useState('');

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    setView(initialTab === 'register' ? 'signup' : initialTab === 'forgot' ? 'forgot' : 'login');
    resetForm();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialTab, isOpen]);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (cooldown > 0) {
      timer = setInterval(() => setCooldown((prev) => Math.max(0, prev - 1)), 1000);
    }
    return () => clearInterval(timer);
  }, [cooldown]);

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setOtp('');
    setVerificationToken('');
    setSignupStep(1);
    setForgotStep(1);
    setErrorMessage('');
    setSuccessMessage('');
  };

  const switchView = (newView: PageView) => {
    setView(newView);
    resetForm();
  };

  if (!isOpen) return null;

  // 1. LOGIN
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    if (!email.trim() || !password) {
      setErrorMessage('Please enter both your email address and password.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Invalid email or password. Please try again.');
      }
      login(data.access_token, data.user);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to sign in.');
    } finally {
      setLoading(false);
    }
  };

  // 2. SEND OTP
  const handleSendOtp = async (purpose: 'register' | 'forgot_password') => {
    setErrorMessage('');
    setSuccessMessage('');
    if (!email.trim() || !email.includes('@')) {
      setErrorMessage('Please enter a valid email address.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), purpose }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to send OTP code.');
      }
      setSuccessMessage(`A 6-digit verification code was sent to ${email.trim()}.`);
      setCooldown(data.cooldown_seconds || data.resend_after_seconds || 60);

      if (purpose === 'register') {
        setSignupStep(2);
      } else {
        setForgotStep(2);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to send OTP.');
    } finally {
      setLoading(false);
    }
  };

  // 3. VERIFY OTP (Forgot Password)
  const handleVerifyOtpForForgot = async () => {
    setErrorMessage('');
    setSuccessMessage('');
    if (!otp || otp.trim().length !== 6) {
      setErrorMessage('Please enter the 6-digit code sent to your email.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), otp: otp.trim(), purpose: 'forgot_password' }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Invalid or expired verification code.');
      }
      setVerificationToken(data.verification_token);
      setSuccessMessage('Code verified. Set your new password below.');
      setForgotStep(3);
    } catch (err: any) {
      setErrorMessage(err.message || 'Invalid or expired code.');
    } finally {
      setLoading(false);
    }
  };

  // 4. CREATE ACCOUNT
  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    if (!otp || otp.trim().length !== 6) {
      setErrorMessage('Please enter the 6-digit verification code.');
      return;
    }
    if (password.length < 6) {
      setErrorMessage('Password must be at least 6 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter.');
      return;
    }
    setLoading(true);
    try {
      let token = verificationToken;
      if (!token) {
        const verifyRes = await fetch(`${API_BASE}/api/auth/verify-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.trim(), otp: otp.trim(), purpose: 'register' }),
        });
        const verifyData = await verifyRes.json();
        if (!verifyRes.ok) {
          throw new Error(verifyData.detail || 'Invalid or expired OTP code.');
        }
        token = verifyData.verification_token;
      }

      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password, verification_token: token }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed. Please try again.');
      }
      setSuccessMessage('Account created successfully! Please sign in.');
      setTimeout(() => switchView('login'), 1500);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to complete registration.');
    } finally {
      setLoading(false);
    }
  };

  // 5. RESET PASSWORD
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    if (password.length < 6) {
      setErrorMessage('Password must be at least 6 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), new_password: password, verification_token: verificationToken }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Password reset failed.');
      }
      setSuccessMessage('Password updated successfully! Please sign in.');
      setTimeout(() => switchView('login'), 1500);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-cover bg-center bg-no-repeat animate-in fade-in duration-200"
      style={{ backgroundImage: `url(${heroImage})` }}
      onClick={onClose}
    >
      {/* Dark overlay & blur */}
      <div className="absolute inset-0 bg-[#060a14]/80 backdrop-blur-[4px]" />

      <div
        className="relative z-10 w-full max-w-[440px] bg-[#0c1322]/90 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-7 sm:p-9 text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white hover:bg-slate-800/60 rounded-xl transition-colors"
        >
          <X size={18} />
        </button>

        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-7">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 p-0.5 shadow-lg shadow-blue-500/30 flex items-center justify-center mb-3">
            <div className="w-full h-full bg-[#080d1a] rounded-[14px] flex items-center justify-center">
              <TrendingUp size={22} className="text-cyan-400" />
            </div>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
            FinAdvisor<span className="text-cyan-400 font-extrabold">-X</span>
          </h1>

          <h2 className="text-lg font-semibold text-slate-200 mt-2">
            {view === 'login' && 'Welcome back'}
            {view === 'signup' && 'Create your account'}
            {view === 'forgot' && 'Reset your password'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {view === 'login' && 'Sign in to access your private financial intelligence'}
            {view === 'signup' && 'Get started with verified AI wealth planning'}
            {view === 'forgot' && 'Follow the quick steps to restore your access'}
          </p>
        </div>

        {/* Alerts */}
        {errorMessage && (
          <div className="mb-5 p-3 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start gap-2.5 text-xs text-red-300">
            <AlertCircle size={16} className="shrink-0 mt-0.5 text-red-400" />
            <span>{errorMessage}</span>
          </div>
        )}
        {successMessage && (
          <div className="mb-5 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-start gap-2.5 text-xs text-cyan-300">
            <CheckCircle2 size={16} className="shrink-0 mt-0.5 text-cyan-400" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* 1. LOGIN */}
        {view === 'login' && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Email address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-medium text-slate-300">Password</label>
                <button
                  type="button"
                  onClick={() => switchView('forgot')}
                  className="text-xs font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-10 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-sm shadow-lg shadow-cyan-500/20 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              {loading ? (
                <RefreshCw size={16} className="animate-spin text-slate-950" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>

            <div className="text-center pt-2">
              <p className="text-xs text-slate-400">
                New user?{' '}
                <button
                  type="button"
                  onClick={() => switchView('signup')}
                  className="text-cyan-400 font-semibold hover:text-cyan-300 transition-colors"
                >
                  Create account
                </button>
              </p>
            </div>
          </form>
        )}

        {/* 2. SIGN UP */}
        {view === 'signup' && (
          <div>
            {signupStep === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Email address</label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@example.com"
                      required
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleSendOtp('register')}
                  disabled={loading || !email.trim()}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-sm shadow-lg shadow-cyan-500/20 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <RefreshCw size={16} className="animate-spin text-slate-950" />
                  ) : (
                    <>
                      <span>Send OTP</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            )}

            {signupStep === 2 && (
              <form onSubmit={handleCreateAccount} className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-medium text-slate-300">Enter 6-digit OTP</label>
                    <span className="text-[11px] text-slate-500 font-mono truncate max-w-[140px]">{email}</span>
                  </div>
                  <div className="relative">
                    <KeyRound size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type="text"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="000000"
                      autoFocus
                      required
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-4 text-sm text-center tracking-[8px] font-mono text-cyan-300 outline-none transition-colors"
                    />
                  </div>
                  <div className="flex items-center justify-between mt-1 text-xs">
                    <button
                      type="button"
                      onClick={() => setSignupStep(1)}
                      className="text-slate-400 hover:text-slate-200"
                    >
                      Change email
                    </button>
                    <button
                      type="button"
                      disabled={cooldown > 0 || loading}
                      onClick={() => handleSendOtp('register')}
                      className="text-cyan-400 hover:text-cyan-300 disabled:opacity-50"
                    >
                      {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">New password (min 6 chars)</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={6}
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-10 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Confirm password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={6}
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-10 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading || otp.length !== 6}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-sm shadow-lg shadow-cyan-500/20 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <RefreshCw size={16} className="animate-spin text-slate-950" />
                  ) : (
                    <>
                      <span>Create Account</span>
                      <Sparkles size={16} />
                    </>
                  )}
                </button>
              </form>
            )}

            <div className="text-center pt-3">
              <p className="text-xs text-slate-400">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => switchView('login')}
                  className="text-cyan-400 font-semibold hover:text-cyan-300 transition-colors"
                >
                  Sign in
                </button>
              </p>
            </div>
          </div>
        )}

        {/* 3. FORGOT PASSWORD */}
        {view === 'forgot' && (
          <div>
            {forgotStep === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Registered email</label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@example.com"
                      required
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleSendOtp('forgot_password')}
                  disabled={loading || !email.trim()}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-sm shadow-lg shadow-cyan-500/20 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <RefreshCw size={16} className="animate-spin text-slate-950" />
                  ) : (
                    <>
                      <span>Send OTP</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            )}

            {forgotStep === 2 && (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-medium text-slate-300">Enter 6-digit OTP</label>
                    <span className="text-[11px] text-slate-500 font-mono truncate max-w-[140px]">{email}</span>
                  </div>
                  <div className="relative">
                    <KeyRound size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type="text"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="000000"
                      autoFocus
                      required
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-4 text-sm text-center tracking-[8px] font-mono text-cyan-300 outline-none transition-colors"
                    />
                  </div>
                  <div className="flex items-center justify-between mt-1 text-xs">
                    <button
                      type="button"
                      onClick={() => setForgotStep(1)}
                      className="text-slate-400 hover:text-slate-200"
                    >
                      Change email
                    </button>
                    <button
                      type="button"
                      disabled={cooldown > 0 || loading}
                      onClick={() => handleSendOtp('forgot_password')}
                      className="text-cyan-400 hover:text-cyan-300 disabled:opacity-50"
                    >
                      {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
                    </button>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleVerifyOtpForForgot}
                  disabled={loading || otp.length !== 6}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-sm shadow-lg shadow-cyan-500/20 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <RefreshCw size={16} className="animate-spin text-slate-950" />
                  ) : (
                    <>
                      <span>Verify OTP</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            )}

            {forgotStep === 3 && (
              <form onSubmit={handleResetPassword} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">New password (min 6 chars)</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={6}
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-10 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Confirm new password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={6}
                      className="w-full bg-[#080d19]/80 border border-slate-700/70 focus:border-cyan-400 rounded-xl py-2.5 pl-10 pr-10 text-sm text-white placeholder:text-slate-500 outline-none transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-sm shadow-lg shadow-cyan-500/20 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <RefreshCw size={16} className="animate-spin text-slate-950" />
                  ) : (
                    <>
                      <span>Reset Password</span>
                      <Sparkles size={16} />
                    </>
                  )}
                </button>
              </form>
            )}

            <div className="text-center pt-3">
              <button
                type="button"
                onClick={() => switchView('login')}
                className="text-xs text-slate-400 hover:text-cyan-300 transition-colors"
              >
                ← Back to Login
              </button>
            </div>
          </div>
        )}

        {/* Security assurance */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-center gap-1.5 text-[11px] text-slate-500">
          <ShieldCheck size={13} className="text-cyan-400" />
          <span>AES-256 encrypted multi-tenant workspace</span>
        </div>

      </div>
    </div>
  );
};

export default AuthModal;
