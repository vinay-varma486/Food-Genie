import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { apiClient } from './api';
import { FoodRestrictionCard } from './FoodRestrictionCard';
import {
  ArrowLeft, TrendingUp, TrendingDown, Scale, Sparkles, Check,
  Bookmark, Loader2, AlertCircle, MessageSquare
} from 'lucide-react';

const GOAL_META = {
  weight_gain: {
    title: 'Weight Gain Planner',
    subtitle: 'Build healthy mass with nutrient-dense calories, complete protein, and balanced meals.',
    icon: TrendingUp,
    calorieOffset: 350,
  },
  weight_loss: {
    title: 'Weight Loss Planner',
    subtitle: 'Sustainable fat loss with high-fiber, high-satiety, protein-rich wholefoods.',
    icon: TrendingDown,
    calorieOffset: -400,
  },
  maintain_weight: {
    title: 'Weight Maintenance Planner',
    subtitle: 'Steady daily energy, micronutrient balance, and long-term metabolic wellness.',
    icon: Scale,
    calorieOffset: 0,
  },
};

const ALLERGY_OPTIONS = ['Peanuts', 'Dairy', 'Gluten', 'Eggs', 'Soy', 'Shellfish'];
const CONDITION_OPTIONS = ['Diabetes', 'Hypertension (BP)', 'Thyroid', 'PCOS', 'Kidney Stones', 'GERD / Acidity'];

export const GoalPlannerView = ({
  initialGoal = 'weight_gain',
  onBack,
  onAskGenie,
  onOpenAuth,
}) => {
  const { user, token, isAuthenticated, updateProfile } = useAuth();
  const [goal, setGoal] = useState(initialGoal);
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [heightCm, setHeightCm] = useState('');
  const [currentWeight, setCurrentWeight] = useState('');
  const [targetWeight, setTargetWeight] = useState('');
  const [activityLevel, setActivityLevel] = useState('moderate');
  const [dietaryPreference, setDietaryPreference] = useState('vegetarian');
  const [weeklyBudget, setWeeklyBudget] = useState('1000');
  const [selectedAllergies, setSelectedAllergies] = useState([]);
  const [selectedConditions, setSelectedConditions] = useState([]);

  const [plan, setPlan] = useState(null);
  const [restrictions, setRestrictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setGoal(initialGoal);
  }, [initialGoal]);

  useEffect(() => {
    if (user?.profile) {
      const p = user.profile;
      if (p.age) setAge(String(p.age));
      if (p.gender) setGender(p.gender);
      if (p.height_cm) setHeightCm(String(p.height_cm));
      if (p.weight_kg) setCurrentWeight(String(p.weight_kg));
      if (p.target_weight_kg) setTargetWeight(String(p.target_weight_kg));
      if (p.activity_level) setActivityLevel(p.activity_level);
      if (p.dietary_preference) setDietaryPreference(p.dietary_preference);
      if (p.monthly_food_budget) setWeeklyBudget(String(Math.round(p.monthly_food_budget / 4)));
      if (Array.isArray(p.allergies)) {
        setSelectedAllergies(p.allergies.map((a) => a.allergen_name));
      }
      if (p.health_conditions) {
        try {
          const parsed = JSON.parse(p.health_conditions);
          if (Array.isArray(parsed)) setSelectedConditions(parsed);
        } catch (_) {
          setSelectedConditions(p.health_conditions.split(',').map((s) => s.trim()).filter(Boolean));
        }
      }
    }
  }, [user]);

  const toggleItem = (list, setList, val) => {
    setList(list.includes(val) ? list.filter((i) => i !== val) : [...list, val]);
  };

  // Estimated daily calorie calculation (Mifflin-St Jeor estimate when age/weight/height given)
  const estimateDailyCalories = () => {
    const w = parseFloat(currentWeight);
    const h = parseFloat(heightCm);
    const a = parseInt(age, 10);
    if (!w || !h || !a) return null;
    const s = gender === 'female' ? -161 : 5;
    const bmr = 10 * w + 6.25 * h - 5 * a + s;
    const mult = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725 }[activityLevel] || 1.55;
    const tdee = Math.round(bmr * mult);
    const offset = GOAL_META[goal]?.calorieOffset || 0;
    return Math.max(1200, tdee + offset);
  };

  const handleGenerate = async (e) => {
    e?.preventDefault();
    if (loading) return;
    setError(null);
    setSavedMsg(null);

    const aNum = Number(age);
    const wNum = Number(currentWeight);
    const hNum = Number(heightCm);
    const bNum = Number(weeklyBudget) || 1000;

    if (!aNum || aNum < 10 || aNum > 110) {
      setError('Please enter a valid age between 10 and 110.');
      return;
    }
    if (!wNum || wNum < 25 || wNum > 300) {
      setError('Please enter your current weight in kg (25–300).');
      return;
    }
    if (!hNum || hNum < 100 || hNum > 250) {
      setError('Please enter your height in cm (100–250).');
      return;
    }
    if (bNum <= 0) {
      setError('Weekly budget must be greater than ₹0.');
      return;
    }

    setLoading(true);
    try {
      const [dietRes, restRes] = await Promise.all([
        apiClient.generateAIBudgetDiet(
          {
            budget_inr: bNum,
            budget_duration: 'weekly',
            custom_days: 7,
            dietary_preference: dietaryPreference,
            health_goal: goal,
            allergies: selectedAllergies,
            number_of_people: 1,
            age: aNum,
            weight_kg: wNum,
            target_weight_kg: targetWeight ? Number(targetWeight) : null,
            height_cm: hNum,
            activity_level: activityLevel,
            location: user?.profile?.city || 'Hyderabad',
          },
          token
        ),
        apiClient.analyzeRestrictions(
          {
            allergies: selectedAllergies,
            medical_conditions: selectedConditions,
            dietary_preference: dietaryPreference,
            language: 'en',
          },
          token
        ),
      ]);
      setPlan(dietRes);
      setRestrictions(restRes?.restrictions || []);

      if (isAuthenticated && updateProfile) {
        await updateProfile({
          age: aNum,
          gender: gender || null,
          weight_kg: wNum,
          target_weight_kg: targetWeight ? Number(targetWeight) : null,
          height_cm: hNum,
          activity_level: activityLevel,
          dietary_preference: dietaryPreference,
          health_goals: goal,
          health_conditions: selectedConditions.join(', ') || null,
          allergies: selectedAllergies,
          daily_calorie_target: estimateDailyCalories() || 2000,
        }).catch(() => {});
      }
    } catch (err) {
      setError(err.message || 'Could not generate your personalized goal plan.');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePlan = async () => {
    if (!plan || saving) return;
    if (!isAuthenticated) {
      if (onOpenAuth) onOpenAuth();
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await apiClient.saveAIBudgetPlan(plan, token);
      setSavedMsg('Plan saved to My Saved Plans!');
    } catch (err) {
      setError(err.message || 'Failed to save plan.');
    } finally {
      setSaving(false);
    }
  };

  const meta = GOAL_META[goal] || GOAL_META.weight_gain;
  const MetaIcon = meta.icon;
  const estCalories = estimateDailyCalories();
  const sampleDay = plan?.daily_plans?.[0];

  return (
    <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div>
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-royal/70 hover:text-royal mb-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-royal text-lime-electric flex items-center justify-center">
              <MetaIcon className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-royal">{meta.title}</h1>
              <p className="text-xs sm:text-sm text-royal/70">{meta.subtitle}</p>
            </div>
          </div>

          <div className="flex gap-1.5 bg-white p-1 rounded-full border border-lavender-border">
            {Object.entries(GOAL_META).map(([gKey, gVal]) => (
              <button
                key={gKey}
                type="button"
                onClick={() => setGoal(gKey)}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-colors ${
                  goal === gKey ? 'bg-royal text-white' : 'text-royal/70 hover:text-royal'
                }`}
              >
                {gVal.title.replace(' Planner', '')}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Input Form */}
        <form onSubmit={handleGenerate} className="lg:col-span-5 fg-card p-6 space-y-4">
          <h2 className="font-bold text-base text-royal border-b border-lavender-mist pb-2">
            Your Health Details
          </h2>

          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Age *</label>
              <input
                type="number"
                min="10"
                max="110"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="e.g. 25"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Gender (Optional)</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
              >
                <option value="">Prefer not to say</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2.5">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Height (cm) *</label>
              <input
                type="number"
                min="100"
                max="250"
                value={heightCm}
                onChange={(e) => setHeightCm(e.target.value)}
                placeholder="170"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Weight (kg) *</label>
              <input
                type="number"
                step="0.1"
                min="25"
                max="300"
                value={currentWeight}
                onChange={(e) => setCurrentWeight(e.target.value)}
                placeholder="60"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Target (kg)</label>
              <input
                type="number"
                step="0.1"
                min="25"
                max="300"
                value={targetWeight}
                onChange={(e) => setTargetWeight(e.target.value)}
                placeholder="66"
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Activity Level</label>
              <select
                value={activityLevel}
                onChange={(e) => setActivityLevel(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-xs font-semibold text-royal focus:outline-none focus:border-royal"
              >
                <option value="sedentary">Sedentary</option>
                <option value="light">Light Activity</option>
                <option value="moderate">Moderate Activity</option>
                <option value="active">Very Active</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1">Weekly Budget (₹)</label>
              <input
                type="number"
                min="100"
                step="50"
                value={weeklyBudget}
                onChange={(e) => setWeeklyBudget(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1.5">Dietary Preference</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'vegetarian', label: 'Vegetarian' },
                { id: 'non-vegetarian', label: 'Non-Veg' },
                { id: 'vegan', label: 'Vegan' },
              ].map((d) => (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => setDietaryPreference(d.id)}
                  className={`py-2 rounded-xl text-xs font-bold border ${
                    dietaryPreference === d.id
                      ? 'bg-royal text-white border-royal'
                      : 'bg-lavender-light text-royal border-lavender-border'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1.5">Food Allergies</label>
            <div className="flex flex-wrap gap-1.5">
              {ALLERGY_OPTIONS.map((alg) => (
                <button
                  key={alg}
                  type="button"
                  onClick={() => toggleItem(selectedAllergies, setSelectedAllergies, alg)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${
                    selectedAllergies.includes(alg)
                      ? 'bg-rose-600 text-white border-rose-600'
                      : 'bg-lavender-light text-royal/80 border-lavender-border'
                  }`}
                >
                  {alg}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase text-royal/70 mb-1.5">Health Conditions / Restrictions</label>
            <div className="flex flex-wrap gap-1.5">
              {CONDITION_OPTIONS.map((cond) => (
                <button
                  key={cond}
                  type="button"
                  onClick={() => toggleItem(selectedConditions, setSelectedConditions, cond)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${
                    selectedConditions.includes(cond)
                      ? 'bg-amber-600 text-white border-amber-600'
                      : 'bg-lavender-light text-royal/80 border-lavender-border'
                  }`}
                >
                  {cond}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-royal hover:bg-royal-light text-white font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin text-lime-electric" /> : <Sparkles className="w-4 h-4 text-lime-electric" />}
            <span>{loading ? 'Building Your Plan...' : 'Generate Personalized Plan'}</span>
          </button>
        </form>

        {/* Results Panel */}
        <div className="lg:col-span-7 space-y-5">
          {!plan ? (
            <div className="fg-card p-8 text-center space-y-2">
              <p className="font-bold text-base text-royal">Enter your details to build your plan</p>
              <p className="text-xs text-royal/70">
                Genie will organize your meals across Breakfast, Morning Snack, Lunch, Evening Snack, and Dinner with estimated nutrition and cost.
              </p>
            </div>
          ) : (
            <>
              {/* Metrics & Save Actions */}
              <div className="fg-card p-5 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="font-bold text-base text-royal">{plan.title}</h3>
                    <p className="text-xs text-royal/70">
                      {estCalories ? `Estimated Daily Energy Target: ~${estCalories} kcal` : 'Balanced daily nutrition'} • Estimated Plan Cost: ₹{plan.total_expenditure_inr}/week
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={handleSavePlan}
                      disabled={saving}
                      className="px-3.5 py-2 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold flex items-center gap-1.5"
                    >
                      {savedMsg ? <Check className="w-3.5 h-3.5 text-lime-electric" /> : <Bookmark className="w-3.5 h-3.5 text-lime-electric" />}
                      <span>{saving ? 'Saving...' : savedMsg ? 'Saved' : 'Save Plan'}</span>
                    </button>
                    {onAskGenie && (
                      <button
                        type="button"
                        onClick={() =>
                          onAskGenie(
                            `I am ${age} years old, ${currentWeight}kg, ${heightCm}cm (${dietaryPreference}). Please review my ${goal.replace('_', ' ')} plan and suggest tips.`
                          )
                        }
                        className="px-3.5 py-2 rounded-xl bg-lavender-mist hover:bg-lavender-dark text-royal text-xs font-bold border border-lavender-border flex items-center gap-1.5"
                      >
                        <MessageSquare className="w-3.5 h-3.5" />
                        <span>Ask Genie</span>
                      </button>
                    )}
                  </div>
                </div>

                {savedMsg && (
                  <p className="text-xs font-bold text-lime-dark bg-lime-electric/25 px-3 py-1.5 rounded-xl">
                    {savedMsg}
                  </p>
                )}

                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center">
                  <div className="bg-lavender-light p-3 rounded-xl border border-lavender-border">
                    <span className="block text-[10px] font-bold uppercase text-royal/55">Avg Calories</span>
                    <span className="font-extrabold text-base text-royal">{Math.round(plan.avg_daily_calories)} kcal</span>
                  </div>
                  <div className="bg-lime-electric/25 p-3 rounded-xl border border-lime-electric">
                    <span className="block text-[10px] font-bold uppercase text-royal-deep">Avg Protein</span>
                    <span className="font-extrabold text-base text-royal-deep">{plan.avg_daily_protein_g}g</span>
                  </div>
                  <div className="bg-lavender-light p-3 rounded-xl border border-lavender-border">
                    <span className="block text-[10px] font-bold uppercase text-royal/55">Avg Carbs</span>
                    <span className="font-extrabold text-base text-royal">{plan.avg_daily_carbs_g}g</span>
                  </div>
                  <div className="bg-lavender-light p-3 rounded-xl border border-lavender-border">
                    <span className="block text-[10px] font-bold uppercase text-royal/55">Avg Fats</span>
                    <span className="font-extrabold text-base text-royal">{plan.avg_daily_fat_g}g</span>
                  </div>
                  <div className="bg-lavender-light p-3 rounded-xl border border-lavender-border">
                    <span className="block text-[10px] font-bold uppercase text-royal/55">Daily Cost (Est.)</span>
                    <span className="font-extrabold text-base text-royal">₹{plan.daily_cost_per_person_inr}</span>
                  </div>
                </div>
              </div>

              {/* 5-Meal Categorized Schedule Table */}
              {sampleDay && (
                <div className="fg-card p-5 space-y-3">
                  <h3 className="font-bold text-base text-royal">
                    Daily 5-Category Meal Schedule (Sample Day 1 — Estimated Values)
                  </h3>
                  <div className="overflow-x-auto rounded-xl border border-lavender-border">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="bg-royal text-white uppercase tracking-wider font-bold">
                          <th className="py-2.5 px-3">Meal</th>
                          <th className="py-2.5 px-3">Food</th>
                          <th className="py-2.5 px-3">Quantity</th>
                          <th className="py-2.5 px-3 text-right">Calories</th>
                          <th className="py-2.5 px-3 text-right">Protein</th>
                          <th className="py-2.5 px-3 text-right">Est. Cost</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-lavender-mist">
                        {['breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner'].map((mk) => {
                          const m = sampleDay.meals[mk];
                          if (!m) return null;
                          return (
                            <tr key={mk} className="hover:bg-lavender-light">
                              <td className="py-2.5 px-3 font-bold text-royal whitespace-nowrap">{m.meal_label}</td>
                              <td className="py-2.5 px-3 font-semibold text-royal-deep">{m.food_name}</td>
                              <td className="py-2.5 px-3 text-royal/75">{m.quantity}</td>
                              <td className="py-2.5 px-3 text-right font-bold">{Math.round(m.nutrients.calories_kcal)} kcal</td>
                              <td className="py-2.5 px-3 text-right font-bold text-lime-dark">{m.nutrients.protein_g}g</td>
                              <td className="py-2.5 px-3 text-right font-bold text-royal">₹{m.estimated_cost_inr}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Foods to Limit / Avoid */}
              {restrictions.length > 0 && (
                <div className="fg-card p-5 space-y-3">
                  <h3 className="font-bold text-base text-royal">Foods to Limit or Avoid</h3>
                  <div className="space-y-2.5">
                    {restrictions.map((r, idx) => (
                      <FoodRestrictionCard key={idx} restriction={r} />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoalPlannerView;

