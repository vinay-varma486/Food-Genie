import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE_URL } from './api';
import { useLanguage } from './LanguageContext';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const { setLanguage } = useLanguage();
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem('foodgenie_jwt') || null;
    } catch (_) {
      return null;
    }
  });
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    let active = true;
    async function loadUser() {
      if (!token) {
        if (active) {
          setUser(null);
          setIsLoading(false);
        }
        return;
      }

      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!active) return;

        if (res.ok) {
          const userData = await res.json();
          setUser(userData);
          if (userData.profile?.preferred_language) {
            setLanguage(userData.profile.preferred_language);
          }
        } else {
          setToken(null);
          setUser(null);
          try {
            localStorage.removeItem('foodgenie_jwt');
          } catch (_) {}
        }
      } catch (e) {
        console.warn('Could not verify session with server:', e);
      } finally {
        if (active) setIsLoading(false);
      }
    }

    loadUser();
    return () => {
      active = false;
    };
  }, [token]);

  const login = async (email, password) => {
    setIsLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Invalid email or password');
      }

      const data = await res.json();
      const jwtToken = data.access_token;
      setToken(jwtToken);
      try {
        localStorage.setItem('foodgenie_jwt', jwtToken);
      } catch (_) {}

      const userRes = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      if (userRes.ok) {
        const userData = await userRes.json();
        setUser(userData);
        if (userData.profile?.preferred_language) {
          setLanguage(userData.profile.preferred_language);
        }
      }
      return true;
    } catch (err) {
      setAuthError(err.message || 'Sign in failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async ({ fullName, email, password, confirmPassword }) => {
    setIsLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: (fullName || '').trim(),
          email: email.trim(),
          password,
          confirm_password: confirmPassword ?? password,
        }),
      });

      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(body.detail || 'Registration failed');
      }
      return body;
    } catch (err) {
      setAuthError(err.message || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOtp = async (email, otp) => {
    setIsLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), otp: otp.trim() }),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || 'OTP verification failed');
      }

      const jwtToken = data.access_token;
      setToken(jwtToken);
      try {
        localStorage.setItem('foodgenie_jwt', jwtToken);
      } catch (_) {}

      const userRes = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      if (userRes.ok) {
        const userData = await userRes.json();
        setUser(userData);
        if (userData.profile?.preferred_language) {
          setLanguage(userData.profile.preferred_language);
        }
      }
      return data;
    } catch (err) {
      setAuthError(err.message || 'OTP verification failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const resendOtp = async (email) => {
    setAuthError(null);
    const res = await fetch(`${API_BASE_URL}/auth/resend-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim() }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = data.detail || 'Could not resend verification OTP';
      setAuthError(msg);
      throw new Error(msg);
    }
    return data;
  };

  const logout = async () => {
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (_) {}
    }
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem('foodgenie_jwt');
    } catch (_) {}
  };

  const updateProfile = async (profileData) => {
    if (!token) throw new Error('Please sign in to save your profile.');
    const res = await fetch(`${API_BASE_URL}/profile/me`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(profileData),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Profile update failed');
    }

    const updatedProfile = await res.json();
    // Refresh full user object so full_name stays synchronized
    const meRes = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (meRes.ok) {
      const fullUser = await meRes.json();
      setUser(fullUser);
    } else {
      setUser((prev) => (prev ? { ...prev, profile: updatedProfile } : null));
    }
    return updatedProfile;
  };

  const displayName =
    user?.full_name?.trim() ||
    (user?.email
      ? user.email.split('@')[0].replace(/[._-]/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
      : 'Friend');

  return (
    <AuthContext.Provider
      value={{
        user,
        displayName,
        token,
        isAuthenticated: Boolean(user && token),
        isLoading,
        authError,
        setAuthError,
        login,
        register,
        verifyOtp,
        resendOtp,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
