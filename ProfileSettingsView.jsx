import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { apiClient } from './api';
import { ArrowLeft, User, Check, Loader2, AlertCircle, LogOut, Trash2, LogIn } from 'lucide-react';

export const ProfileSettingsView = ({ onBack, onOpenAuth, onProfileSaved }) => {
  const { user, displayName, token, isAuthenticated, updateProfile, logout } = useAuth();

  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [weightKg, setWeightKg] = useState('');
  const [targetWeightKg, setTargetWeightKg] = useState('');
  const [heightCm, setHeightCm] = useState('');
  const [activityLevel, setActivityLevel] = useState('moderate');
  const [healthGoal, setHealthGoal] = useState('maintain_weight');
  const [dietaryPref, setDietaryPref] = useState('vegetarian');
  const [budgetInr, setBudgetInr] = useState('4000');
  const [city, setCity] = useState('Hyderabad');
  const [allergiesText, setAllergiesText] = useState('');
  const [conditionsText, setConditionsText] = useState('');

  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      const p = user.profile;
      if (p) {
        setAge(p.age ? String(p.age) : '');
        setGender(p.gender || '');
        setWeightKg(p.weight_kg ? String(p.weight_kg) : '');
        setTargetWeightKg(p.target_weight_kg ? String(p.target_weight_kg) : '');
        setHeightCm(p.height_cm ? String(p.height_cm) : '');
        setActivityLevel(p.activity_level || 'moderate');
        setHealthGoal(p.health_goals || 'maintain_weight');
        setDietaryPref(p.dietary_preference || 'vegetarian');
        setBudgetInr(p.monthly_food_budget ? String(p.monthly_food_budget) : '4000');
        setCity(p.city || 'Hyderabad');
        setConditionsText(p.health_conditions || '');
        setAllergiesText(Array.isArray(p.allergies) ? p.allergies.map((a) => a.allergen_name).join(', ') : '');
      }
    }
  }, [user]);

  const handleSave = async (e) => {
    e.preventDefault();
    if (saving || !isAuthenticated) return;
    setError(null);
    setSavedSuccess(false);

    if (age && (Number(age) < 10 || Number(age) > 110)) {
      setError('Please enter a valid age between 10 and 110.');
      return;
    }
    if (weightKg && (Number(weightKg) < 25 || Number(weightKg) > 300)) {
      setError('Weight must be between 25 kg and 300 kg.');
      return;
    }
    if (heightCm && (Number(heightCm) < 100 || Number(heightCm) > 250)) {
      setError('Height must be between 100 cm and 250 cm.');
      return;
    }

    setSaving(true);
    try {
      const allergiesArr = allergiesText
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      await updateProfile({
        full_name: fullName.trim() || null,
        age: age ? parseInt(age, 10) : null,
        gender: gender || null,
        weight_kg: weightKg ? parseFloat(weightKg) : null,
        target_weight_kg: targetWeightKg ? parseFloat(targetWeightKg) : null,
        height_cm: heightCm ? parseFloat(heightCm) : null,
        activity_level: activityLevel,
        health_goals: healthGoal,
        dietary_preference: dietaryPref,
        monthly_food_budget: budgetInr ? parseFloat(budgetInr) : 4000,
        city: city.trim() || 'Hyderabad',
        health_conditions: conditionsText.trim() || null,
        allergies: allergiesArr,
      });
      setSavedSuccess(true);
      if (onProfileSaved) onProfileSaved();
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Could not update profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Delete your FoodGenie account and all saved history permanently?')) return;
    setDeleting(true);
    setError(null);
    try {
      await apiClient.delete('/profile/me', token);
      await logout();
      if (onBack) onBack();
    } catch (err) {
      setError(err.message || 'Could not delete account.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div>
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-royal/70 hover:text-royal mb-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-royal text-lime-electric flex items-center justify-center">
            <User className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-royal">
              Profile and Settings
            </h1>
            <p className="text-xs sm:text-sm text-royal/70">
              Personalize how Genie tailors recommendations, allergies, and budget plans
            </p>
          </div>
        </div>
      </div>

      {!isAuthenticated ? (
        <div className="fg-card p-8 text-center space-y-3">
          <p className="font-bold text-base text-royal">Sign in to manage your profile</p>
          <p className="text-xs text-royal/70">
            Save your personal name, health goal, dietary preferences, and allergies securely.
          </p>
          <button
            type="button"
            onClick={onOpenAuth}
            className="px-5 py-2.5 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold inline-flex items-center gap-2"
          >
            <LogIn className="w-4 h-4 text-lime-electric" />
            <span>Sign In / Register</span>
          </button>
        </div>
      ) : (
        <form onSubmit={handleSave} className="fg-card p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {savedSuccess && (
            <div className="p-3 rounded-xl bg-lime-electric/30 border border-lime-electric text-xs font-bold text-royal-deep flex items-center gap-2">
              <Check className="w-4 h-4" />
              <span>Profile updated successfully!</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Display Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder={displayName}
                className="w-full px-3.5 py-2.5 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Email</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="w-full px-3.5 py-2.5 rounded-xl bg-lavender-mist/60 border border-lavender-border text-sm text-royal/60"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Age</label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="25"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Gender (Opt.)</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-xs font-bold text-royal"
              >
                <option value="">Unspecified</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Height (cm)</label>
              <input
                type="number"
                value={heightCm}
                onChange={(e) => setHeightCm(e.target.value)}
                placeholder="170"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Weight (kg)</label>
              <input
                type="number"
                step="0.1"
                value={weightKg}
                onChange={(e) => setWeightKg(e.target.value)}
                placeholder="65"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Target Weight (kg)</label>
              <input
                type="number"
                step="0.1"
                value={targetWeightKg}
                onChange={(e) => setTargetWeightKg(e.target.value)}
                placeholder="68"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Activity Level</label>
              <select
                value={activityLevel}
                onChange={(e) => setActivityLevel(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-xs font-bold text-royal"
              >
                <option value="sedentary">Sedentary</option>
                <option value="light">Light</option>
                <option value="moderate">Moderate</option>
                <option value="active">Active</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">City</label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Health Goal</label>
              <select
                value={healthGoal}
                onChange={(e) => setHealthGoal(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-xs font-bold text-royal"
              >
                <option value="weight_gain">Weight Gain</option>
                <option value="weight_loss">Weight Loss</option>
                <option value="maintain_weight">Weight Maintenance</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Diet Preference</label>
              <select
                value={dietaryPref}
                onChange={(e) => setDietaryPref(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-xs font-bold text-royal"
              >
                <option value="vegetarian">Vegetarian</option>
                <option value="non-vegetarian">Non-Vegetarian</option>
                <option value="vegan">Vegan</option>
                <option value="flexitarian">Flexitarian</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Monthly Budget (₹)</label>
              <input
                type="number"
                min="200"
                step="100"
                value={budgetInr}
                onChange={(e) => setBudgetInr(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Food Allergies (comma separated)</label>
              <input
                type="text"
                value={allergiesText}
                onChange={(e) => setAllergiesText(e.target.value)}
                placeholder="e.g. Peanuts, Dairy"
                className="w-full px-3.5 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Health Conditions (comma separated)</label>
              <input
                type="text"
                value={conditionsText}
                onChange={(e) => setConditionsText(e.target.value)}
                placeholder="e.g. Diabetes, Thyroid"
                className="w-full px-3.5 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full py-3 rounded-xl bg-royal hover:bg-royal-light text-white font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {saving && <Loader2 className="w-4 h-4 animate-spin text-lime-electric" />}
            <span>{saving ? 'Updating Profile...' : 'Save & Update Profile'}</span>
          </button>

          <div className="pt-4 border-t border-lavender-mist flex flex-wrap items-center justify-between gap-3">
            <button
              type="button"
              onClick={async () => {
                await logout();
                if (onBack) onBack();
              }}
              className="px-4 py-2 rounded-xl bg-lavender-mist hover:bg-lavender-dark text-royal text-xs font-bold flex items-center gap-1.5"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </button>

            <button
              type="button"
              onClick={handleDeleteAccount}
              disabled={deleting}
              className="px-4 py-2 rounded-xl border border-red-200 text-red-700 hover:bg-red-50 text-xs font-bold flex items-center gap-1.5"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{deleting ? 'Deleting...' : 'Delete Account'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default ProfileSettingsView;

