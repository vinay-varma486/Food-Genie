import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import {
  Sparkles,
  X,
  Mail,
  Lock,
  User,
  KeyRound,
  AlertCircle,
  ArrowRight,
  Loader2,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';

export const AuthModal = ({ isOpen, onClose, initialMode = 'login', onAuthSuccess }) => {
  const { login, register, verifyOtp, resendOtp, updateProfile, authError, setAuthError } = useAuth();
  const [mode, setMode] = useState(initialMode);
  const [regStep, setRegStep] = useState('form'); // 'form' | 'otp' | 'optional_profile'
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [localError, setLocalError] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);

  // Registration & Login fields
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // OTP Verification state
  const [otp, setOtp] = useState('');
  const [otpExpiresSec, setOtpExpiresSec] = useState(0);
  const [resendCooldownSec, setResendCooldownSec] = useState(0);

  // Optional Health Profile state (Step 3 after OTP verification)
  const [age, setAge] = useState('');
  const [heightCm, setHeightCm] = useState('');
  const [weightKg, setWeightKg] = useState('');
  const [targetWeightKg, setTargetWeightKg] = useState('');
  const [healthGoal, setHealthGoal] = useState('maintain_weight');
  const [dietaryPref, setDietaryPref] = useState('vegetarian');
  const [allergiesText, setAllergiesText] = useState('');
  const [budgetPeriod, setBudgetPeriod] = useState('weekly');
  const [budgetAmount, setBudgetAmount] = useState('');

  useEffect(() => {
    if (isOpen) {
      setLocalError(null);
      setAuthError(null);
      setStatusMessage(null);
    }
  }, [isOpen, setAuthError]);

  useEffect(() => {
    if (!isOpen || regStep !== 'otp') return;
    const timer = setInterval(() => {
      setOtpExpiresSec((prev) => (prev > 0 ? prev - 1 : 0));
      setResendCooldownSec((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [isOpen, regStep]);

  if (!isOpen) return null;

  const formatSec = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  };

  const resetToMode = (nextMode) => {
    setMode(nextMode);
    setRegStep('form');
    setLocalError(null);
    setAuthError(null);
    setStatusMessage(null);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLocalError(null);
    setAuthError(null);

    const cleanEmail = email.trim();
    if (!cleanEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setLocalError('Please enter a valid email address.');
      return;
    }
    if (password.length < 6) {
      setLocalError('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);
    try {
      await login(cleanEmail, password);
      if (onAuthSuccess) onAuthSuccess('login');
      onClose();
    } catch (_) {
      // authError displays details cleanly (including pending OTP message if unverified)
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLocalError(null);
    setAuthError(null);
    setStatusMessage(null);

    const cleanName = fullName.trim();
    const cleanEmail = email.trim();

    if (!cleanName || cleanName.length < 2) {
      setLocalError('Please enter your full name.');
      return;
    }
    if (!cleanEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setLocalError('Please enter a valid email address.');
      return;
    }
    if (password.length < 6) {
      setLocalError('Password must be at least 6 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setLocalError('Password and Confirm Password do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await register({
        fullName: cleanName,
        email: cleanEmail,
        password,
        confirmPassword,
      });
      setOtp('');
      setOtpExpiresSec(res?.expires_in_seconds || 300);
      setResendCooldownSec(res?.resend_cooldown_seconds || 60);
      setStatusMessage(res?.message || `Verification OTP sent to ${cleanEmail}.`);
      setRegStep('otp');
    } catch (_) {
      // authError set cleanly
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLocalError(null);
    setAuthError(null);

    const cleanOtp = otp.trim();
    if (!/^\d{6}$/.test(cleanOtp)) {
      setLocalError('Please enter the 6-digit verification OTP sent to your email.');
      return;
    }

    setLoading(true);
    try {
      await verifyOtp(email.trim(), cleanOtp);
      setStatusMessage('Email verified and account activated!');
      setRegStep('optional_profile');
      if (onAuthSuccess) onAuthSuccess('register');
    } catch (_) {
      // Displayed via authError
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (resending || resendCooldownSec > 0) return;
    setResending(true);
    setLocalError(null);
    setAuthError(null);
    try {
      const res = await resendOtp(email.trim());
      setOtpExpiresSec(res?.expires_in_seconds || 300);
      setResendCooldownSec(res?.resend_cooldown_seconds || 60);
      setStatusMessage(`A fresh OTP has been sent to ${email.trim()}.`);
    } catch (_) {} finally {
      setResending(false);
    }
  };

  const handleSaveOptionalProfile = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLocalError(null);

    let monthlyBudget = undefined;
    if (budgetAmount && Number(budgetAmount) > 0) {
      const raw = Number(budgetAmount);
      monthlyBudget = budgetPeriod === 'daily' ? raw * 30 : Math.round((raw / 7) * 30);
    }

    setLoading(true);
    try {
      const allergiesArr = allergiesText
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      await updateProfile({
        age: age ? parseInt(age, 10) : null,
        height_cm: heightCm ? parseFloat(heightCm) : null,
        weight_kg: weightKg ? parseFloat(weightKg) : null,
        target_weight_kg: targetWeightKg ? parseFloat(targetWeightKg) : null,
        health_goals: healthGoal,
        dietary_preference: dietaryPref,
        allergies: allergiesArr,
        ...(monthlyBudget ? { monthly_food_budget: monthlyBudget } : {}),
      });
      onClose();
    } catch (err) {
      setLocalError(err.message || 'Could not save profile preferences.');
    } finally {
      setLoading(false);
    }
  };

  const errorMessage = localError || authError;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#230852]/55 backdrop-blur-sm">
      <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-[#D8C5FF] overflow-hidden max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="bg-[#351078] p-5 text-white flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#230852] border border-[#C6FF00]/40 flex items-center justify-center text-[#C6FF00]">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-display font-bold text-lg">
                {mode === 'login'
                  ? 'Welcome Back'
                  : regStep === 'otp'
                  ? 'Verify Email OTP'
                  : regStep === 'optional_profile'
                  ? 'Optional Health Profile'
                  : 'Create FoodGenie Account'}
              </h3>
              <p className="text-xs text-[#E5DAFB]">
                {mode === 'login'
                  ? 'Sign in with email and password'
                  : regStep === 'otp'
                  ? 'Enter the 6-digit code emailed to you'
                  : regStep === 'optional_profile'
                  ? 'Personalize Genie (optional — you can skip)'
                  : 'Verified registration with email OTP'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-full hover:bg-white/10 text-white"
            aria-label="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Mode Switcher */}
        {regStep === 'form' && (
          <div className="flex border-b border-[#D8C5FF] bg-[#FAF7FF] p-1.5 gap-1 flex-shrink-0">
            <button
              type="button"
              onClick={() => resetToMode('login')}
              className={`flex-1 py-2 text-xs font-bold rounded-xl transition-colors ${
                mode === 'login' ? 'bg-white text-[#351078] shadow-xs border border-[#D8C5FF]' : 'text-[#5B4B7A] hover:text-[#351078]'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => resetToMode('register')}
              className={`flex-1 py-2 text-xs font-bold rounded-xl transition-colors ${
                mode === 'register' ? 'bg-white text-[#351078] shadow-xs border border-[#D8C5FF]' : 'text-[#5B4B7A] hover:text-[#351078]'
              }`}
            >
              Register
            </button>
          </div>
        )}

        <div className="p-6 space-y-4 overflow-y-auto">
          {statusMessage && (
            <div className="p-3 bg-[#EEF8FC] border border-[#ADD8E6] rounded-xl flex items-start gap-2 text-xs text-[#230852]">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#16A34A]" />
              <span>{statusMessage}</span>
            </div>
          )}

          {errorMessage && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-red-500" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* LOGIN FORM */}
          {mode === 'login' && (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5B4B7A] mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#5B4B7A] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-sm text-[#230852] focus:outline-none focus:border-[#351078]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5B4B7A] mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#5B4B7A] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Minimum 6 characters"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-sm text-[#230852] focus:outline-none focus:border-[#351078]"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white font-bold text-sm shadow-xs flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-[#C6FF00]" />
                    <span>Signing in...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <ArrowRight className="w-4 h-4 text-[#C6FF00]" />
                  </>
                )}
              </button>
            </form>
          )}

          {/* REGISTER STEP 1: DETAILS */}
          {mode === 'register' && regStep === 'form' && (
            <form onSubmit={handleRegisterSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5B4B7A] mb-1">
                  Full Name *
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#5B4B7A] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g., Ananya Sharma"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-sm text-[#230852] focus:outline-none focus:border-[#351078]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5B4B7A] mb-1">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#5B4B7A] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-sm text-[#230852] focus:outline-none focus:border-[#351078]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5B4B7A] mb-1">
                  Password *
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#5B4B7A] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Minimum 6 characters"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-sm text-[#230852] focus:outline-none focus:border-[#351078]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5B4B7A] mb-1">
                  Confirm Password *
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#5B4B7A] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter your password"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-sm text-[#230852] focus:outline-none focus:border-[#351078]"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white font-bold text-sm shadow-xs flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-[#C6FF00]" />
                    <span>Sending Verification OTP...</span>
                  </>
                ) : (
                  <>
                    <span>Send OTP &amp; Continue</span>
                    <ArrowRight className="w-4 h-4 text-[#C6FF00]" />
                  </>
                )}
              </button>
            </form>
          )}

          {/* REGISTER STEP 2: OTP VERIFICATION */}
          {mode === 'register' && regStep === 'otp' && (
            <form onSubmit={handleVerifyOtp} className="space-y-4">
              <div className="p-3.5 rounded-xl bg-[#F2ECFF] border border-[#D8C5FF] text-xs text-[#230852] space-y-1">
                <p>
                  Enter the 6-digit verification code sent to <strong>{email}</strong>.
                </p>
                <p className="font-bold text-[#351078]">
                  Expires in: {otpExpiresSec > 0 ? formatSec(otpExpiresSec) : 'Expired — please resend'}
                </p>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5B4B7A] mb-1.5">
                  6-Digit Verification OTP
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-[#5B4B7A] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    required
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="123456"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-base font-extrabold tracking-[0.35em] text-[#351078] focus:outline-none focus:border-[#351078]"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-[#C6FF00]" />
                    <span>Verifying OTP...</span>
                  </>
                ) : (
                  <>
                    <span>Verify &amp; Activate Account</span>
                    <ArrowRight className="w-4 h-4 text-[#C6FF00]" />
                  </>
                )}
              </button>

              <div className="flex items-center justify-between text-xs pt-1">
                <button
                  type="button"
                  onClick={() => setRegStep('form')}
                  className="text-[#5B4B7A] hover:text-[#351078] font-semibold"
                >
                  Change Email
                </button>
                <button
                  type="button"
                  onClick={handleResendOtp}
                  disabled={resending || resendCooldownSec > 0}
                  className="inline-flex items-center gap-1 font-bold text-[#351078] disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${resending ? 'animate-spin' : ''}`} />
                  <span>
                    {resendCooldownSec > 0
                      ? `Resend OTP in ${resendCooldownSec}s`
                      : 'Resend OTP'}
                  </span>
                </button>
              </div>
            </form>
          )}

          {/* REGISTER STEP 3: OPTIONAL HEALTH & BUDGET PROFILE */}
          {mode === 'register' && regStep === 'optional_profile' && (
            <form onSubmit={handleSaveOptionalProfile} className="space-y-3">
              <p className="text-xs text-[#5B4B7A]">
                Your account is active! Optionally add health &amp; budget preferences below so Genie tailors nutrition advice for you:
              </p>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Age (Optional)</label>
                  <input
                    type="number"
                    min="10"
                    max="110"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="Years"
                    className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs text-[#230852]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Height (cm, Opt.)</label>
                  <input
                    type="number"
                    min="100"
                    max="250"
                    value={heightCm}
                    onChange={(e) => setHeightCm(e.target.value)}
                    placeholder="cm"
                    className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs text-[#230852]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Weight (kg, Opt.)</label>
                  <input
                    type="number"
                    min="25"
                    max="300"
                    step="0.5"
                    value={weightKg}
                    onChange={(e) => setWeightKg(e.target.value)}
                    placeholder="Current kg"
                    className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs text-[#230852]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Target Weight (Opt.)</label>
                  <input
                    type="number"
                    min="25"
                    max="300"
                    step="0.5"
                    value={targetWeightKg}
                    onChange={(e) => setTargetWeightKg(e.target.value)}
                    placeholder="Target kg"
                    className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs text-[#230852]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Health Goal (Opt.)</label>
                  <select
                    value={healthGoal}
                    onChange={(e) => setHealthGoal(e.target.value)}
                    className="w-full px-2.5 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs font-semibold text-[#230852]"
                  >
                    <option value="maintain_weight">Weight Maintenance</option>
                    <option value="weight_loss">Weight Loss</option>
                    <option value="weight_gain">Weight Gain</option>
                    <option value="muscle_building">Muscle Building</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Diet Pref (Opt.)</label>
                  <select
                    value={dietaryPref}
                    onChange={(e) => setDietaryPref(e.target.value)}
                    className="w-full px-2.5 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs font-semibold text-[#230852]"
                  >
                    <option value="vegetarian">Vegetarian</option>
                    <option value="non-vegetarian">Non-Vegetarian</option>
                    <option value="vegan">Vegan</option>
                    <option value="flexitarian">Flexitarian</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Budget Period (Opt.)</label>
                  <select
                    value={budgetPeriod}
                    onChange={(e) => setBudgetPeriod(e.target.value)}
                    className="w-full px-2.5 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs font-semibold text-[#230852]"
                  >
                    <option value="daily">Daily Food Budget</option>
                    <option value="weekly">Weekly Food Budget</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">Budget Amount (₹)</label>
                  <input
                    type="number"
                    min="50"
                    value={budgetAmount}
                    onChange={(e) => setBudgetAmount(e.target.value)}
                    placeholder={budgetPeriod === 'daily' ? 'e.g., 150' : 'e.g., 1000'}
                    className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs text-[#230852]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase text-[#5B4B7A] mb-1">
                  Food Allergies (Optional, comma-separated)
                </label>
                <input
                  type="text"
                  value={allergiesText}
                  onChange={(e) => setAllergiesText(e.target.value)}
                  placeholder="e.g., Peanuts, Lactose"
                  className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs text-[#230852]"
                />
              </div>

              <div className="flex items-center gap-2 pt-1">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 py-2.5 rounded-xl border border-[#D8C5FF] text-xs font-bold text-[#5B4B7A] hover:bg-[#FAF7FF]"
                >
                  Skip for Now
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-2.5 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold"
                >
                  {loading ? 'Saving...' : 'Save Profile'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
