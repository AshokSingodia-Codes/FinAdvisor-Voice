import React, { useState, useEffect } from 'react';
import { 
  X, 
  Mail, 
  Lock, 
  KeyRound, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle, 
  Eye, 
  EyeOff, 
  TrendingUp, 
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'signin' | 'register' | 'forgot';
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, initialTab = 'signin' }) => {
  const { login } = useAuth();
  
  const [tab, setTab] = useState<'signin' | 'register' | 'forgot'>(initialTab);
  
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
    setTab(initialTab);
    resetForm();
  }, [initialTab, isOpen]);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (cooldown > 0) {
      timer = setInterval(() => {
        setCooldown(prev => Math.max(0, prev - 1));
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

  const switchTab = (newTab: 'signin' | 'register' | 'forgot') => {
    setTab(newTab);
    resetForm();
  };

  if (!isOpen) return null;

  // --- Handlers ---

  // 1. Sign In
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
        body: JSON.stringify({ email: email.trim(), password })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Sign in failed. Please check your credentials.');
      }

      login(data.access_token, data.user);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to sign in.');
    } finally {
      setLoading(false);
    }
  };

  // 2. Send OTP (for Register or Forgot Password)
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
        body: JSON.stringify({ email: email.trim(), purpose })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to send OTP.');
      }

      setSuccessMessage(`A 6-digit OTP has been sent to ${email.trim()}.`);
      setCooldown(data.cooldown_seconds || 60);

      if (purpose === 'register') {
        setRegStep(2);
      } else {
        setForgotStep(2);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to send OTP.');
    } finally {
      setLoading(false);
    }
  };

  // 3. Verify OTP
  const handleVerifyOtp = async (purpose: 'register' | 'forgot_password') => {
    setErrorMessage('');
    setSuccessMessage('');
    if (!otp || otp.trim().length !== 6) {
      setErrorMessage('Please enter the 6-digit OTP sent to your email.');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), otp: otp.trim(), purpose })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'OTP verification failed.');
      }

      setVerificationToken(data.verification_token);
      setSuccessMessage('OTP verified! Now create your password.');

      if (purpose === 'register') {
        setRegStep(3);
      } else {
        setForgotStep(3);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Invalid or expired OTP.');
    } finally {
      setLoading(false);
    }
  };

  // 4. Create Account (Register Step 3)
  const handleRegisterAccount = async (e: React.FormEvent) => {
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
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          password,
          verification_token: verificationToken
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed.');
      }

      setSuccessMessage('Account created successfully! Please sign in with your password.');
      setTimeout(() => {
        switchTab('signin');
      }, 1500);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to complete registration.');
    } finally {
      setLoading(false);
    }
  };

  // 5. Reset Password (Forgot Step 3)
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
      const res = await fetch(`${API_BASE}/api/auth/forgot-password/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          new_password: password,
          verification_token: verificationToken
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Password reset failed.');
      }

      setSuccessMessage('Password updated successfully! Please sign in.');
      setTimeout(() => {
        switchTab('signin');
      }, 1500);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-md bg-bgCard border border-borderDim rounded-2xl shadow-2xl overflow-hidden p-6 sm:p-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-textDim hover:text-textMain hover:bg-borderDim/50 rounded-xl transition-colors cursor-pointer"
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accentPrimary to-accentHover flex items-center justify-center shadow-md">
            <TrendingUp size={22} className="text-[#0d0f14]" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-textMain tracking-tight">FinAdvisor-X</h2>
            <p className="text-xs text-textDim">Secure Financial Intelligence Platform</p>
          </div>
        </div>

        {/* Dynamic Alerts */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start gap-2.5 text-xs text-red-400">
            <AlertCircle size={16} className="shrink-0 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-2.5 text-xs text-emerald-400">
            <CheckCircle2 size={16} className="shrink-0 mt-0.5" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* ----------------- TAB: SIGN IN ----------------- */}
        {tab === 'signin' && (
          <div>
            <div className="mb-5">
              <h3 className="text-base font-semibold text-textMain">Welcome Back</h3>
              <p className="text-xs text-textDim mt-0.5">Sign in to access your private financial memory and models.</p>
            </div>

            <form onSubmit={handleSignIn} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-textDim mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    required
                    className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-4 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-medium text-textDim">Password</label>
                  <button
                    type="button"
                    onClick={() => switchTab('forgot')}
                    className="text-xs text-accentPrimary hover:underline cursor-pointer"
                  >
                    Forgot Password?
                  </button>
                </div>
                <div className="relative">
                  <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-11 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-textDim hover:text-textMain cursor-pointer"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2.5 px-4 rounded-xl text-sm shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading ? (
                  <RefreshCw size={16} className="animate-spin" />
                ) : (
                  <>
                    <span>Sign In</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center text-xs text-textDim border-t border-borderDim pt-4">
              Don't have an account?{' '}
              <button
                onClick={() => switchTab('register')}
                className="text-accentPrimary font-semibold hover:underline cursor-pointer"
              >
                Create New Account
              </button>
            </div>
          </div>
        )}

        {/* ----------------- TAB: CREATE NEW ACCOUNT ----------------- */}
        {tab === 'register' && (
          <div>
            <div className="mb-5">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-textMain">Create New Account</h3>
                <span className="text-[11px] font-mono text-accentPrimary bg-accentPrimary/10 border border-accentPrimary/20 px-2 py-0.5 rounded-full">
                  Step {regStep} of 3
                </span>
              </div>
              <p className="text-xs text-textDim mt-0.5">
                {regStep === 1 && 'Enter your email ID to receive a secure verification OTP.'}
                {regStep === 2 && 'Enter the 6-digit OTP sent to your email.'}
                {regStep === 3 && 'Choose a strong password to secure your account.'}
              </p>
            </div>

            {/* Step 1: Email */}
            {regStep === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-textDim mb-1.5">Email Address</label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@company.com"
                      required
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-4 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleSendOtp('register')}
                  disabled={loading || !email.trim()}
                  className="w-full bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2.5 px-4 rounded-xl text-sm shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Send OTP</span><ArrowRight size={16} /></>}
                </button>
              </div>
            )}

            {/* Step 2: OTP */}
            {regStep === 2 && (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-medium text-textDim">Enter 6-digit OTP</label>
                    <span className="text-[11px] text-textDim font-mono">{email}</span>
                  </div>
                  <div className="relative">
                    <KeyRound size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type="text"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="123456"
                      autoFocus
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-4 py-2.5 text-center tracking-[8px] font-mono text-base font-bold text-accentPrimary placeholder:tracking-normal placeholder:font-sans placeholder:text-xs placeholder:text-textDim/40 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <button
                    type="button"
                    onClick={() => setRegStep(1)}
                    className="text-textDim hover:text-textMain cursor-pointer"
                  >
                    Change Email
                  </button>
                  <button
                    type="button"
                    disabled={cooldown > 0 || loading}
                    onClick={() => handleSendOtp('register')}
                    className="text-accentPrimary hover:underline disabled:opacity-50 disabled:no-underline cursor-pointer"
                  >
                    {cooldown > 0 ? `Resend OTP in ${cooldown}s` : 'Resend OTP'}
                  </button>
                </div>

                <button
                  type="button"
                  onClick={() => handleVerifyOtp('register')}
                  disabled={loading || otp.length !== 6}
                  className="w-full bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2.5 px-4 rounded-xl text-sm shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Verify OTP</span><ArrowRight size={16} /></>}
                </button>
              </div>
            )}

            {/* Step 3: Password */}
            {regStep === 3 && (
              <form onSubmit={handleRegisterAccount} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-textDim mb-1.5">Password (min 6 characters)</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={6}
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-11 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-textDim hover:text-textMain cursor-pointer"
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-textDim mb-1.5">Confirm Password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-11 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-textDim hover:text-textMain cursor-pointer"
                    >
                      {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2.5 px-4 rounded-xl text-sm shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Complete Account Creation</span><Sparkles size={16} /></>}
                </button>
              </form>
            )}

            <div className="mt-6 text-center text-xs text-textDim border-t border-borderDim pt-4">
              Already have an account?{' '}
              <button
                onClick={() => switchTab('signin')}
                className="text-accentPrimary font-semibold hover:underline cursor-pointer"
              >
                Sign In
              </button>
            </div>
          </div>
        )}

        {/* ----------------- TAB: FORGOT PASSWORD ----------------- */}
        {tab === 'forgot' && (
          <div>
            <div className="mb-5">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-textMain">Reset Password</h3>
                <span className="text-[11px] font-mono text-accentPrimary bg-accentPrimary/10 border border-accentPrimary/20 px-2 py-0.5 rounded-full">
                  Step {forgotStep} of 3
                </span>
              </div>
              <p className="text-xs text-textDim mt-0.5">
                {forgotStep === 1 && 'Enter your registered email address to receive a recovery OTP.'}
                {forgotStep === 2 && 'Enter the 6-digit OTP code to verify your identity.'}
                {forgotStep === 3 && 'Enter and confirm your new password.'}
              </p>
            </div>

            {/* Step 1: Registered Email */}
            {forgotStep === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-textDim mb-1.5">Registered Email</label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@company.com"
                      required
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-4 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleSendOtp('forgot_password')}
                  disabled={loading || !email.trim()}
                  className="w-full bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2.5 px-4 rounded-xl text-sm shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Send Recovery OTP</span><ArrowRight size={16} /></>}
                </button>
              </div>
            )}

            {/* Step 2: OTP */}
            {forgotStep === 2 && (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-medium text-textDim">Enter 6-digit Recovery OTP</label>
                    <span className="text-[11px] text-textDim font-mono">{email}</span>
                  </div>
                  <div className="relative">
                    <KeyRound size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type="text"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="123456"
                      autoFocus
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-4 py-2.5 text-center tracking-[8px] font-mono text-base font-bold text-accentPrimary placeholder:tracking-normal placeholder:font-sans placeholder:text-xs placeholder:text-textDim/40 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <button
                    type="button"
                    onClick={() => setForgotStep(1)}
                    className="text-textDim hover:text-textMain cursor-pointer"
                  >
                    Change Email
                  </button>
                  <button
                    type="button"
                    disabled={cooldown > 0 || loading}
                    onClick={() => handleSendOtp('forgot_password')}
                    className="text-accentPrimary hover:underline disabled:opacity-50 disabled:no-underline cursor-pointer"
                  >
                    {cooldown > 0 ? `Resend OTP in ${cooldown}s` : 'Resend OTP'}
                  </button>
                </div>

                <button
                  type="button"
                  onClick={() => handleVerifyOtp('forgot_password')}
                  disabled={loading || otp.length !== 6}
                  className="w-full bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2.5 px-4 rounded-xl text-sm shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Verify OTP</span><ArrowRight size={16} /></>}
                </button>
              </div>
            )}

            {/* Step 3: New Password */}
            {forgotStep === 3 && (
              <form onSubmit={handleResetPassword} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-textDim mb-1.5">New Password (min 6 characters)</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={6}
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-11 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-textDim hover:text-textMain cursor-pointer"
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-textDim mb-1.5">Confirm New Password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-textDim" />
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      className="w-full bg-bgMain border border-borderDim rounded-xl pl-10 pr-11 py-2.5 text-sm text-textMain placeholder:text-textDim/50 focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-textDim hover:text-textMain cursor-pointer"
                    >
                      {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2.5 px-4 rounded-xl text-sm shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Update Password</span><Sparkles size={16} /></>}
                </button>
              </form>
            )}

            <div className="mt-6 text-center text-xs text-textDim border-t border-borderDim pt-4">
              Remember your password?{' '}
              <button
                onClick={() => switchTab('signin')}
                className="text-accentPrimary font-semibold hover:underline cursor-pointer"
              >
                Back to Sign In
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
