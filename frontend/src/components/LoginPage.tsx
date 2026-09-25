import React, { useState, useEffect } from 'react';
import {
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
  TrendingUp,
  Sparkles,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../config';
import heroImage from '../assets/hero-bg.png';

type Tab = 'signin' | 'register' | 'forgot';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();

  const [tab, setTab] = useState<Tab>('signin');

  // Registration multi-step: 1 = Email, 2 = OTP, 3 = Password
  const [regStep, setRegStep] = useState<1 | 2 | 3>(1);
  // Forgot password multi-step: 1 = Email, 2 = OTP, 3 = New Password
  const [forgotStep, setForgotStep] = useState<1 | 2 | 3>(1);

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [verificationToken, setVerificationToken] = useState('');

  // Password visibility
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Feedback states
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Resend cooldown timer
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (cooldown > 0) {
      timer = setInterval(() => {
        setCooldown((prev) => Math.max(0, prev - 1));
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [cooldown]);

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setOtp('');
    setVerificationToken('');
    setRegStep(1);
    setForgotStep(1);
    setErrorMessage('');
    setSuccessMessage('');
  };

  const switchTab = (newTab: Tab) => {
    setTab(newTab);
    resetForm();
  };

  // ----- Handlers -----

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    if (!email || !password) {
      setErrorMessage('Please enter both email and password.');
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
      if (!res.ok) throw new Error(data.detail || 'Sign in failed. Please check your credentials.');
      login(data.access_token, data.user);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to sign in.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendOtp = async (purpose: 'register' | 'forgot_password') => {
    setErrorMessage('');
    setSuccessMessage('');
    if (!email || !email.includes('@')) {
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
      if (!res.ok) throw new Error(data.detail || 'Failed to send OTP.');
      setSuccessMessage(`A 6-digit code has been sent to ${email.trim()}.`);
      setCooldown(data.cooldown_seconds || data.resend_after_seconds || 60);
      purpose === 'register' ? setRegStep(2) : setForgotStep(2);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to send OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (purpose: 'register' | 'forgot_password') => {
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
        body: JSON.stringify({ email: email.trim(), otp: otp.trim(), purpose }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'OTP verification failed.');
      setVerificationToken(data.verification_token);
      setSuccessMessage('Verified. Now set your password.');
      purpose === 'register' ? setRegStep(3) : setForgotStep(3);
    } catch (err: any) {
      setErrorMessage(err.message || 'Invalid or expired code.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    if (password.length < 6) return setErrorMessage('Password must be at least 6 characters long.');
    if (password !== confirmPassword) return setErrorMessage('Passwords do not match. Please re-enter.');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password, verification_token: verificationToken }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Registration failed.');
      setSuccessMessage('Account created. Redirecting to sign in...');
      setTimeout(() => switchTab('signin'), 1500);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to complete registration.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    if (password.length < 6) return setErrorMessage('Password must be at least 6 characters long.');
    if (password !== confirmPassword) return setErrorMessage('Passwords do not match. Please re-enter.');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), new_password: password, verification_token: verificationToken }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Password reset failed.');
      setSuccessMessage('Password updated. Redirecting to sign in...');
      setTimeout(() => switchTab('signin'), 1500);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  // ----- Style helpers -----
  const inputClass =
    'w-full bg-transparent border-0 border-b border-slate-700 focus:border-blue-400 outline-none py-2.5 text-sm text-slate-100 placeholder:text-slate-600 transition-colors';
  const labelClass = 'block text-xs font-medium text-slate-400 mb-2';
  const primaryBtn =
    'w-full bg-gradient-to-r from-blue-500 to-blue-400 text-slate-950 font-semibold py-3 px-4 rounded-lg text-sm shadow-lg shadow-blue-500/20 hover:brightness-110 active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer';

  const tabBtn = (t: Tab, label: string) => (
    <button
      onClick={() => switchTab(t)}
      className={`pb-3 text-sm transition-colors cursor-pointer ${
        tab === t
          ? 'text-slate-100 font-medium border-b-2 border-blue-400'
          : 'text-slate-500 hover:text-slate-300 border-b-2 border-transparent'
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="min-h-screen w-full flex bg-[#060a14]">
      {/* ---------------- LEFT: hero / brand panel ---------------- */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <img
          src={heroImage}
          alt=""
          className="absolute inset-0 w-full h-full object-cover"
        />
        {/* Fade the photo into the panel color so it reads as one surface */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#060a14] via-[#060a14]/60 to-[#060a14]/10" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#060a14] via-transparent to-[#060a14]/40" />

        <div className="relative z-10 flex flex-col justify-between w-full p-12 xl:p-16">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-300 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <TrendingUp size={20} className="text-[#060a14]" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight">FinAdvisor-X</span>
          </div>

          <div className="max-w-md">
            <p className="text-[11px] uppercase tracking-[0.2em] text-blue-400/80 font-semibold mb-4">
              Your Financial Copilot
            </p>
            <h1 className="text-4xl xl:text-5xl font-semibold text-white leading-[1.1]">
              Make every rupee<br />
              <span className="italic font-serif text-blue-300">work smarter.</span>
            </h1>
            <p className="mt-5 text-slate-400 text-sm leading-relaxed">
              Personalized financial planning, grounded in your documents and the Indian market.
            </p>
          </div>

          <div className="flex items-center gap-8 text-slate-400">
            <div>
              <div className="text-xl font-semibold text-white">24/7</div>
              <div className="text-xs mt-0.5">AI guidance</div>
            </div>
            <div className="w-px h-8 bg-slate-700" />
            <div>
              <div className="text-xl font-semibold text-white">100%</div>
              <div className="text-xs mt-0.5">Private context</div>
            </div>
            <div className="w-px h-8 bg-slate-700" />
            <div className="flex items-center gap-1.5 text-xs">
              <ShieldCheck size={14} className="text-blue-400" />
              Your data stays isolated to your account
            </div>
          </div>
        </div>
      </div>

      {/* ---------------- RIGHT: auth form panel ---------------- */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-10 bg-[#0a0f1c]">
        <div className="w-full max-w-sm">
          {/* Mobile-only brand mark */}
          <div className="flex lg:hidden items-center gap-3 mb-10">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-300 flex items-center justify-center shadow-md">
              <TrendingUp size={20} className="text-[#060a14]" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight">FinAdvisor-X</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-white tracking-tight">
              {tab === 'signin' && 'Welcome back'}
              {tab === 'register' && 'Create your account'}
              {tab === 'forgot' && 'Reset your password'}
            </h2>
            <p className="text-sm text-slate-500 mt-1.5">
              {tab === 'signin' && 'Sign in to continue to your private workspace.'}
              {tab === 'register' && 'A few quick steps to get you set up.'}
              {tab === 'forgot' && "We'll get you back into your account."}
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-7 border-b border-slate-800 mb-8">
            {tabBtn('signin', 'Sign in')}
            {tabBtn('register', 'Sign up')}
            {tabBtn('forgot', 'Forgot?')}
          </div>

          {/* Alerts */}
          {errorMessage && (
            <div className="mb-5 p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start gap-2.5 text-xs text-red-400">
              <AlertCircle size={15} className="shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}
          {successMessage && (
            <div className="mb-5 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-start gap-2.5 text-xs text-blue-300">
              <CheckCircle2 size={15} className="shrink-0 mt-0.5" />
              <span>{successMessage}</span>
            </div>
          )}

          {/* ---------- SIGN IN ---------- */}
          {tab === 'signin' && (
            <form onSubmit={handleSignIn} className="space-y-6">
              <div>
                <label className={labelClass}>Email address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className={inputClass}
                />
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-medium text-slate-400">Password</label>
                  <button
                    type="button"
                    onClick={() => switchTab('forgot')}
                    className="text-xs text-blue-400 hover:text-blue-300 cursor-pointer"
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Your password"
                    required
                    className={`${inputClass} pr-8`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-0 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300 cursor-pointer"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={loading} className={primaryBtn}>
                {loading ? <RefreshCw size={16} className="animate-spin" /> : (
                  <>
                    <span>Enter workspace</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>

              <p className="text-center text-xs text-slate-500">
                Don&apos;t have an account?{' '}
                <button type="button" onClick={() => switchTab('register')} className="text-blue-400 font-medium hover:text-blue-300 cursor-pointer">
                  Create one
                </button>
              </p>
            </form>
          )}

          {/* ---------- REGISTER ---------- */}
          {tab === 'register' && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 text-[11px] font-mono text-blue-400">
                <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20">Step {regStep} of 3</span>
              </div>

              {regStep === 1 && (
                <div className="space-y-6">
                  <div>
                    <label className={labelClass}>Email address</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      required
                      className={inputClass}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => handleSendOtp('register')}
                    disabled={loading || !email.trim()}
                    className={primaryBtn}
                  >
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : (<><span>Send verification code</span><ArrowRight size={16} /></>)}
                  </button>
                </div>
              )}

              {regStep === 2 && (
                <div className="space-y-6">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-xs font-medium text-slate-400">Enter 6-digit code</label>
                      <span className="text-[11px] text-slate-600 font-mono truncate max-w-[160px]">{email}</span>
                    </div>
                    <input
                      type="text"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="000000"
                      autoFocus
                      className={`${inputClass} text-center tracking-[10px] font-mono text-lg text-blue-300`}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <button type="button" onClick={() => setRegStep(1)} className="text-slate-500 hover:text-slate-300 cursor-pointer">
                      Change email
                    </button>
                    <button
                      type="button"
                      disabled={cooldown > 0 || loading}
                      onClick={() => handleSendOtp('register')}
                      className="text-blue-400 hover:text-blue-300 disabled:opacity-40 disabled:hover:text-blue-400 cursor-pointer"
                    >
                      {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleVerifyOtp('register')}
                    disabled={loading || otp.length !== 6}
                    className={primaryBtn}
                  >
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : (<><span>Verify code</span><ArrowRight size={16} /></>)}
                  </button>
                </div>
              )}

              {regStep === 3 && (
                <form onSubmit={handleRegisterAccount} className="space-y-6">
                  <div>
                    <label className={labelClass}>Create password (min 6 characters)</label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="New password"
                        required
                        minLength={6}
                        className={`${inputClass} pr-8`}
                      />
                      <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-0 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300 cursor-pointer">
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className={labelClass}>Confirm password</label>
                    <div className="relative">
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm password"
                        required
                        className={`${inputClass} pr-8`}
                      />
                      <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-0 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300 cursor-pointer">
                        {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>
                  <button type="submit" disabled={loading} className={primaryBtn}>
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : (<><span>Create account</span><Sparkles size={16} /></>)}
                  </button>
                </form>
              )}

              <p className="text-center text-xs text-slate-500">
                Already have an account?{' '}
                <button type="button" onClick={() => switchTab('signin')} className="text-blue-400 font-medium hover:text-blue-300 cursor-pointer">
                  Sign in
                </button>
              </p>
            </div>
          )}

          {/* ---------- FORGOT PASSWORD ---------- */}
          {tab === 'forgot' && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 text-[11px] font-mono text-blue-400">
                <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20">Step {forgotStep} of 3</span>
              </div>

              {forgotStep === 1 && (
                <div className="space-y-6">
                  <div>
                    <label className={labelClass}>Registered email</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      required
                      className={inputClass}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => handleSendOtp('forgot_password')}
                    disabled={loading || !email.trim()}
                    className={primaryBtn}
                  >
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : (<><span>Send recovery code</span><ArrowRight size={16} /></>)}
                  </button>
                </div>
              )}

              {forgotStep === 2 && (
                <div className="space-y-6">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-xs font-medium text-slate-400">Enter recovery code</label>
                      <span className="text-[11px] text-slate-600 font-mono truncate max-w-[160px]">{email}</span>
                    </div>
                    <input
                      type="text"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="000000"
                      autoFocus
                      className={`${inputClass} text-center tracking-[10px] font-mono text-lg text-blue-300`}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <button type="button" onClick={() => setForgotStep(1)} className="text-slate-500 hover:text-slate-300 cursor-pointer">
                      Change email
                    </button>
                    <button
                      type="button"
                      disabled={cooldown > 0 || loading}
                      onClick={() => handleSendOtp('forgot_password')}
                      className="text-blue-400 hover:text-blue-300 disabled:opacity-40 disabled:hover:text-blue-400 cursor-pointer"
                    >
                      {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleVerifyOtp('forgot_password')}
                    disabled={loading || otp.length !== 6}
                    className={primaryBtn}
                  >
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : (<><span>Verify code</span><ArrowRight size={16} /></>)}
                  </button>
                </div>
              )}

              {forgotStep === 3 && (
                <form onSubmit={handleResetPassword} className="space-y-6">
                  <div>
                    <label className={labelClass}>New password (min 6 characters)</label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="New password"
                        required
                        minLength={6}
                        className={`${inputClass} pr-8`}
                      />
                      <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-0 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300 cursor-pointer">
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className={labelClass}>Confirm new password</label>
                    <div className="relative">
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                        required
                        className={`${inputClass} pr-8`}
                      />
                      <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-0 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300 cursor-pointer">
                        {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>
                  <button type="submit" disabled={loading} className={primaryBtn}>
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : (<><span>Update password</span><Sparkles size={16} /></>)}
                  </button>
                </form>
              )}

              <p className="text-center text-xs text-slate-500">
                Remember your password?{' '}
                <button type="button" onClick={() => switchTab('signin')} className="text-blue-400 font-medium hover:text-blue-300 cursor-pointer">
                  Back to sign in
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
