import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { apiClient } from './api';
import {
  Wallet, ArrowLeft, Sparkles, RefreshCw, Bookmark,
  AlertTriangle, Check, ShoppingBag, Table, Layers, PieChart, Edit2, RotateCcw
} from 'lucide-react';

const LOCATIONS = [
  { id: 'Hyderabad', label: 'Hyderabad' },
  { id: 'Vijayawada', label: 'Vijayawada' },
  { id: 'Bengaluru', label: 'Bengaluru' },
  { id: 'Chennai', label: 'Chennai' },
  { id: 'Mumbai', label: 'Mumbai' },
  { id: 'Delhi', label: 'Delhi' },
];

const HEALTH_GOALS = [
  { id: 'weight_gain', label: 'Weight Gain' },
  { id: 'weight_loss', label: 'Weight Loss' },
  { id: 'maintain_weight', label: 'Maintain Weight' },
];

const ALLERGY_CHIPS = ['Peanuts', 'Dairy', 'Gluten', 'Eggs', 'Soy', 'Shellfish'];

export const BudgetPlannerView = ({ onBack, onOpenAuth, onPlanSaved }) => {
  const { user, token, isAuthenticated } = useAuth();

  const [budgetDuration, setBudgetDuration] = useState('weekly'); // 'daily' | 'weekly' | 'monthly'
  const [budget, setBudget] = useState('1000');
  const [familyMembers, setFamilyMembers] = useState(1);
  const [location, setLocation] = useState('Hyderabad');
  const [dietaryPreference, setDietaryPreference] = useState('vegetarian');
  const [healthGoal, setHealthGoal] = useState('maintain_weight');
  const [selectedAllergies, setSelectedAllergies] = useState([]);
  const [allowOverBudget, setAllowOverBudget] = useState(false);

  const [planData, setPlanData] = useState(null);
  const [editableDays, setEditableDays] = useState([]);
  const [editableGrocery, setEditableGrocery] = useState([]);
  const [editingCell, setEditingCell] = useState(null); // { dayIdx, mealKey }

  const [activeTab, setActiveTab] = useState('weekly_table'); // 'weekly_table' | 'meals' | 'summary' | 'grocery'
  const [activeDayIndex, setActiveDayIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [savingPlan, setSavingPlan] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user?.profile) {
      const p = user.profile;
      if (p.health_goals?.includes('gain')) setHealthGoal('weight_gain');
      else if (p.health_goals?.includes('loss')) setHealthGoal('weight_loss');
      if (p.dietary_preference) setDietaryPreference(p.dietary_preference);
      if (p.city) setLocation(p.city);
      if (Array.isArray(p.allergies)) {
        setSelectedAllergies(p.allergies.map((a) => a.allergen_name));
      }
    }
  }, [user]);

  const handleGeneratePlan = useCallback(async () => {
    const budgetNum = Number(budget);
    if (!budgetNum || budgetNum <= 0) {
      setError('Please enter a valid budget greater than ₹0.');
      return;
    }
    if (loading) return;

    setLoading(true);
    setError(null);
    setSavedSuccess(false);
    try {
      const res = await apiClient.generateAIBudgetDiet(
        {
          budget_inr: budgetNum,
          budget_duration: budgetDuration,
          custom_days: budgetDuration === 'daily' ? 1 : budgetDuration === 'weekly' ? 7 : 30,
          location,
          dietary_preference: dietaryPreference,
          health_goal: healthGoal,
          allergies: selectedAllergies,
          number_of_people: Number(familyMembers),
          allow_over_budget: allowOverBudget,
          language: 'en',
        },
        token
      );
      setPlanData(res);
      setEditableDays(res.daily_plans || []);
      setActiveDayIndex(0);
      const srcGrocery = budgetDuration === 'monthly' ? res.monthly_grocery_list : res.weekly_grocery_list;
      setEditableGrocery((srcGrocery || []).map((g) => ({ ...g })));
    } catch (err) {
      setError(err.message || 'Could not generate budget plan. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [budget, budgetDuration, location, dietaryPreference, healthGoal, selectedAllergies, familyMembers, allowOverBudget, token, loading]);

  useEffect(() => {
    handleGeneratePlan();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSwapMealWithAlt = (dayIdx, mealKey, alt) => {
    const updated = [...editableDays];
    const day = { ...updated[dayIdx], meals: { ...updated[dayIdx].meals } };
    const meal = { ...day.meals[mealKey] };
    meal.food_name = alt.food_name;
    meal.estimated_cost_inr = alt.cost_inr;
    meal.unit_price_inr = Math.round((alt.cost_inr / Math.max(1, familyMembers)) * 100) / 100;
    day.meals[mealKey] = meal;
    day.daily_cost_inr = Math.round(
      Object.values(day.meals).reduce((acc, m) => acc + (m.estimated_cost_inr || 0), 0) * 100
    ) / 100;
    updated[dayIdx] = day;
    setEditableDays(updated);
    setEditingCell(null);
  };

  const handleCustomMealEdit = (dayIdx, mealKey, newName, newCost) => {
    const updated = [...editableDays];
    const day = { ...updated[dayIdx], meals: { ...updated[dayIdx].meals } };
    const meal = { ...day.meals[mealKey] };
    meal.food_name = newName;
    const costVal = Math.max(1, Number(newCost) || meal.estimated_cost_inr);
    meal.estimated_cost_inr = costVal;
    day.meals[mealKey] = meal;
    day.daily_cost_inr = Math.round(
      Object.values(day.meals).reduce((acc, m) => acc + (m.estimated_cost_inr || 0), 0) * 100
    ) / 100;
    updated[dayIdx] = day;
    setEditableDays(updated);
  };

  const handleGroceryQtyChange = (idx, newQty) => {
    const next = [...editableGrocery];
    const item = { ...next[idx], quantity: newQty };
    const match = String(newQty).match(/(\d+(?:\.\d+)?)/);
    if (match) {
      item.total_cost_inr = Math.round(parseFloat(match[1]) * item.unit_price_inr * 100) / 100;
    }
    next[idx] = item;
    setEditableGrocery(next);
  };

  const handleSavePlan = async () => {
    if (!planData || savingPlan) return;
    if (!isAuthenticated) {
      if (onOpenAuth) onOpenAuth();
      return;
    }
    setSavingPlan(true);
    setError(null);
    try {
      const totalExp = editableDays.reduce((s, d) => s + (d.daily_cost_inr || 0), 0);
      await apiClient.saveAIBudgetPlan(
        {
          ...planData,
          daily_plans: editableDays,
          total_expenditure_inr: Math.round(totalExp * 100) / 100,
          weekly_grocery_list: editableGrocery,
        },
        token
      );
      setSavedSuccess(true);
      if (onPlanSaved) onPlanSaved();
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to save budget plan.');
    } finally {
      setSavingPlan(false);
    }
  };

  const totalPlanExp = Math.round(editableDays.reduce((s, d) => s + (d.daily_cost_inr || 0), 0) * 100) / 100;
  const daysShown = editableDays.length || 1;
  const avgDailyExp = Math.round((totalPlanExp / daysShown) * 100) / 100;
  const weeklyEstExp = Math.round((totalPlanExp / daysShown) * 7 * 100) / 100;
  const monthlyEstExp = Math.round((totalPlanExp / daysShown) * 30 * 100) / 100;
  const budgetTargetNum = Number(budget) || 0;
  const remainingBudget = Math.round((budgetTargetNum - totalPlanExp) * 100) / 100;

  const avgCalories = editableDays.length
    ? Math.round(editableDays.reduce((s, d) => s + (d.daily_calories || 0), 0) / editableDays.length)
    : 0;
  const avgProtein = editableDays.length
    ? Math.round((editableDays.reduce((s, d) => s + (d.daily_protein_g || 0), 0) / editableDays.length) * 10) / 10
    : 0;
  const avgCarbs = editableDays.length
    ? Math.round((editableDays.reduce((s, d) => s + (d.daily_carbs_g || 0), 0) / editableDays.length) * 10) / 10
    : 0;
  const avgFat = editableDays.length
    ? Math.round((editableDays.reduce((s, d) => s + (d.daily_fat_g || 0), 0) / editableDays.length) * 10) / 10
    : 0;

  const totalGroceryCost = Math.round(editableGrocery.reduce((s, g) => s + (g.total_cost_inr || 0), 0) * 100) / 100;
  const currentDay = editableDays[activeDayIndex];

  return (
    <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
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
              <Wallet className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-royal">
                Smart Budget Planner
              </h1>
              <p className="text-xs sm:text-sm text-royal/70">
                Daily, weekly, and monthly meal schedules calculated from estimated local prices
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleGeneratePlan}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl bg-lavender-mist hover:bg-lavender-dark text-royal text-xs font-bold border border-lavender-border flex items-center gap-1.5"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>
          {planData && (
            <button
              type="button"
              onClick={handleSavePlan}
              disabled={savingPlan}
              className="px-4 py-2.5 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold flex items-center gap-1.5"
            >
              {savedSuccess ? <Check className="w-3.5 h-3.5 text-lime-electric" /> : <Bookmark className="w-3.5 h-3.5 text-lime-electric" />}
              <span>{savingPlan ? 'Saving...' : savedSuccess ? 'Saved!' : 'Save Plan'}</span>
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {planData?.budget_insufficient && planData.budget_limitation_note && (
        <div className="px-4 py-3 rounded-2xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-bold">Budget Limitation Notice</p>
            <p className="mt-0.5 leading-relaxed">{planData.budget_limitation_note}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Parameters Sidebar */}
        <div className="lg:col-span-4 fg-card p-5 space-y-4">
          <h2 className="font-bold text-base text-royal border-b border-lavender-mist pb-2">
            Budget Settings
          </h2>

          {/* Duration: Daily / Weekly / Monthly */}
          <div>
            <label className="text-[11px] font-bold uppercase text-royal/70 mb-1.5 block">
              Budget Period
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {[
                { id: 'daily', label: 'Daily', defaultAmt: '150' },
                { id: 'weekly', label: 'Weekly', defaultAmt: '1000' },
                { id: 'monthly', label: 'Monthly', defaultAmt: '4000' },
              ].map((d) => (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => {
                    setBudgetDuration(d.id);
                    setBudget(d.defaultAmt);
                  }}
                  className={`py-2 rounded-xl text-xs font-bold border ${
                    budgetDuration === d.id
                      ? 'bg-royal text-white border-royal'
                      : 'bg-lavender-light text-royal border-lavender-border'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Budget Amount */}
          <div>
            <label className="text-[11px] font-bold uppercase text-royal/70 mb-1.5 block">
              Enter {budgetDuration} Budget (₹ INR)
            </label>
            <input
              type="number"
              min="1"
              step="10"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-lavender-light border border-lavender-border text-sm font-bold text-royal focus:outline-none focus:border-royal"
            />
          </div>

          {/* People & City */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-bold uppercase text-royal/70 mb-1.5 block">People</label>
              <select
                value={familyMembers}
                onChange={(e) => setFamilyMembers(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-xs font-bold text-royal focus:outline-none focus:border-royal"
              >
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <option key={n} value={n}>{n} {n === 1 ? 'Person' : 'People'}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[11px] font-bold uppercase text-royal/70 mb-1.5 block">City</label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-lavender-light border border-lavender-border text-xs font-bold text-royal focus:outline-none focus:border-royal"
              >
                {LOCATIONS.map((loc) => (
                  <option key={loc.id} value={loc.id}>{loc.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Diet */}
          <div>
            <label className="text-[11px] font-bold uppercase text-royal/70 mb-1.5 block">Dietary Preference</label>
            <div className="grid grid-cols-3 gap-1.5">
              {[
                { id: 'vegetarian', label: 'Vegetarian' },
                { id: 'non-vegetarian', label: 'Non-Veg' },
                { id: 'vegan', label: 'Vegan' },
              ].map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setDietaryPreference(t.id)}
                  className={`py-2 rounded-xl text-xs font-bold border ${
                    dietaryPreference === t.id
                      ? 'bg-royal text-white border-royal'
                      : 'bg-lavender-light text-royal border-lavender-border'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Goal */}
          <div>
            <label className="text-[11px] font-bold uppercase text-royal/70 mb-1.5 block">Health Goal</label>
            <div className="grid grid-cols-3 gap-1.5">
              {HEALTH_GOALS.map((g) => (
                <button
                  key={g.id}
                  type="button"
                  onClick={() => setHealthGoal(g.id)}
                  className={`py-2 px-1 rounded-xl text-[11px] font-bold border ${
                    healthGoal === g.id
                      ? 'bg-royal text-white border-royal'
                      : 'bg-lavender-light text-royal border-lavender-border'
                  }`}
                >
                  {g.label}
                </button>
              ))}
            </div>
          </div>

          {/* Allergies */}
          <div>
            <label className="text-[11px] font-bold uppercase text-royal/70 mb-1.5 block">Allergies</label>
            <div className="flex flex-wrap gap-1.5">
              {ALLERGY_CHIPS.map((a) => (
                <button
                  key={a}
                  type="button"
                  onClick={() =>
                    setSelectedAllergies((prev) =>
                      prev.includes(a) ? prev.filter((x) => x !== a) : [...prev, a]
                    )
                  }
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border ${
                    selectedAllergies.includes(a)
                      ? 'bg-rose-600 text-white border-rose-600'
                      : 'bg-lavender-light text-royal/80 border-lavender-border'
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          <label className="flex items-center gap-2 text-xs text-royal/80 cursor-pointer pt-1">
            <input
              type="checkbox"
              checked={allowOverBudget}
              onChange={(e) => setAllowOverBudget(e.target.checked)}
              className="rounded border-lavender-border accent-royal"
            />
            <span>Allow meals slightly above budget</span>
          </label>

          <button
            type="button"
            onClick={handleGeneratePlan}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-royal hover:bg-royal-light text-white font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin text-lime-electric" /> : <Sparkles className="w-4 h-4 text-lime-electric" />}
            <span>{loading ? 'Generating Plan...' : 'Generate Budget Plan'}</span>
          </button>
        </div>

        {/* Results Dashboard */}
        <div className="lg:col-span-8 space-y-5">
          {planData && (
            <>
              {/* Expense & Nutrition KPI Strip */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="fg-card p-3.5 text-center">
                  <span className="text-[10px] font-bold uppercase text-royal/55 block">Daily Est. Expense</span>
                  <span className="font-extrabold text-lg text-royal">₹{avgDailyExp}</span>
                </div>
                <div className="fg-card p-3.5 text-center">
                  <span className="text-[10px] font-bold uppercase text-royal/55 block">Weekly Est. Expense</span>
                  <span className="font-extrabold text-lg text-royal">₹{weeklyEstExp}</span>
                </div>
                <div className="fg-card p-3.5 text-center">
                  <span className="text-[10px] font-bold uppercase text-royal/55 block">Monthly Est. Expense</span>
                  <span className="font-extrabold text-lg text-royal">₹{monthlyEstExp}</span>
                </div>
                <div className="fg-card p-3.5 text-center">
                  <span className="text-[10px] font-bold uppercase text-royal/55 block">Budget Balance</span>
                  <span className={`font-extrabold text-lg ${remainingBudget >= 0 ? 'text-lime-dark' : 'text-rose-600'}`}>
                    {remainingBudget >= 0 ? `₹${remainingBudget} left` : `Over ₹${Math.abs(remainingBudget)}`}
                  </span>
                </div>
              </div>

              {/* View Tabs */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1">
                {[
                  { id: 'weekly_table', label: budgetDuration === 'daily' ? 'Daily Schedule' : '7-Day Table', icon: Table },
                  { id: 'meals', label: 'Edit Meals & Details', icon: Layers },
                  { id: 'summary', label: 'Nutrition Summary', icon: PieChart },
                  { id: 'grocery', label: 'Grocery List', icon: ShoppingBag },
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() => setActiveTab(tab.id)}
                      className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 whitespace-nowrap border ${
                        activeTab === tab.id
                          ? 'bg-royal text-white border-royal'
                          : 'bg-white text-royal/75 border-lavender-border hover:bg-lavender-light'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* TAB 1: Weekly/Daily Schedule Table */}
              {activeTab === 'weekly_table' && (
                <div className="fg-card p-5 space-y-3">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <h3 className="font-bold text-base text-royal">
                      Meal Plan Table (Estimated Costs in ₹)
                    </h3>
                    <span className="text-[11px] text-royal/60">
                      Click &quot;Edit Meals &amp; Details&quot; to swap or customize items
                    </span>
                  </div>

                  <div className="overflow-x-auto rounded-xl border border-lavender-border">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="bg-royal text-white uppercase tracking-wider font-bold">
                          <th className="py-2.5 px-3">Day</th>
                          <th className="py-2.5 px-3">Breakfast</th>
                          <th className="py-2.5 px-3">Lunch</th>
                          <th className="py-2.5 px-3">Evening Snack</th>
                          <th className="py-2.5 px-3">Dinner</th>
                          <th className="py-2.5 px-3 text-right">Total Cost</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-lavender-mist">
                        {editableDays.slice(0, 7).map((dp, idx) => {
                          const bf = dp.meals.breakfast;
                          const lunch = dp.meals.lunch;
                          const snack = dp.meals.evening_snack || dp.meals.morning_snack;
                          const din = dp.meals.dinner;
                          return (
                            <tr key={dp.day_number || idx} className="hover:bg-lavender-light">
                              <td className="py-2.5 px-3 font-bold text-royal whitespace-nowrap">
                                {dp.day_label.split(' ')[0]}
                              </td>
                              <td className="py-2.5 px-3">
                                <span className="font-semibold text-royal-deep block">{bf?.food_name}</span>
                                <span className="text-[10px] text-royal/60">{bf?.quantity} • ₹{bf?.estimated_cost_inr}</span>
                              </td>
                              <td className="py-2.5 px-3">
                                <span className="font-semibold text-royal-deep block">{lunch?.food_name}</span>
                                <span className="text-[10px] text-royal/60">{lunch?.quantity} • ₹{lunch?.estimated_cost_inr}</span>
                              </td>
                              <td className="py-2.5 px-3">
                                <span className="font-semibold text-royal-deep block">{snack?.food_name}</span>
                                <span className="text-[10px] text-royal/60">{snack?.quantity} • ₹{snack?.estimated_cost_inr}</span>
                              </td>
                              <td className="py-2.5 px-3">
                                <span className="font-semibold text-royal-deep block">{din?.food_name}</span>
                                <span className="text-[10px] text-royal/60">{din?.quantity} • ₹{din?.estimated_cost_inr}</span>
                              </td>
                              <td className="py-2.5 px-3 text-right font-extrabold text-royal whitespace-nowrap">
                                ₹{dp.daily_cost_inr}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                      <tfoot>
                        <tr className="bg-lavender-mist font-extrabold text-royal border-t border-lavender-border">
                          <td colSpan="5" className="py-2.5 px-3 text-right">
                            Total Plan Estimated Cost ({daysShown} day{daysShown > 1 ? 's' : ''}):
                          </td>
                          <td className="py-2.5 px-3 text-right">₹{totalPlanExp}</td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
              )}

              {/* TAB 2: Meal-by-Meal Editing & Unit Price Breakdown */}
              {activeTab === 'meals' && (
                <div className="space-y-4">
                  {editableDays.length > 1 && (
                    <div className="flex gap-1.5 overflow-x-auto pb-1">
                      {editableDays.slice(0, 7).map((dp, idx) => (
                        <button
                          key={dp.day_number}
                          type="button"
                          onClick={() => setActiveDayIndex(idx)}
                          className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap border ${
                            activeDayIndex === idx
                              ? 'bg-royal text-white border-royal'
                              : 'bg-white text-royal/75 border-lavender-border'
                          }`}
                        >
                          {dp.day_label.split(' ')[0]}
                        </button>
                      ))}
                    </div>
                  )}

                  {currentDay && (
                    <div className="space-y-3">
                      {['breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner'].map((mk) => {
                        const meal = currentDay.meals[mk];
                        if (!meal) return null;
                        const isEditing = editingCell?.dayIdx === activeDayIndex && editingCell?.mealKey === mk;

                        return (
                          <div key={mk} className="fg-card p-4 space-y-2.5">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span className="px-2.5 py-0.5 rounded-lg bg-royal text-white text-[11px] font-bold uppercase">
                                  {meal.meal_label}
                                </span>
                                <span className="text-xs text-royal/65 font-semibold">{meal.quantity}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-royal/70">
                                  Unit: ₹{meal.unit_price_inr ?? meal.estimated_cost_inr} • Total: <strong className="text-royal">₹{meal.estimated_cost_inr}</strong>
                                </span>
                                <button
                                  type="button"
                                  onClick={() =>
                                    setEditingCell(isEditing ? null : { dayIdx: activeDayIndex, mealKey: mk })
                                  }
                                  className="px-2.5 py-1 rounded-lg bg-lavender-mist hover:bg-lavender-dark text-royal text-[11px] font-bold flex items-center gap-1"
                                >
                                  <Edit2 className="w-3 h-3" />
                                  <span>{isEditing ? 'Done' : 'Edit'}</span>
                                </button>
                              </div>
                            </div>

                            {isEditing ? (
                              <div className="p-3 rounded-xl bg-lavender-light border border-lavender-border space-y-2">
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                  <input
                                    type="text"
                                    value={meal.food_name}
                                    onChange={(e) =>
                                      handleCustomMealEdit(activeDayIndex, mk, e.target.value, meal.estimated_cost_inr)
                                    }
                                    className="sm:col-span-2 px-3 py-1.5 rounded-lg bg-white border border-lavender-border text-xs font-bold text-royal"
                                  />
                                  <input
                                    type="number"
                                    min="1"
                                    value={meal.estimated_cost_inr}
                                    onChange={(e) =>
                                      handleCustomMealEdit(activeDayIndex, mk, meal.food_name, e.target.value)
                                    }
                                    className="px-3 py-1.5 rounded-lg bg-white border border-lavender-border text-xs font-bold text-royal"
                                  />
                                </div>
                                {meal.affordable_alternatives?.length > 0 && (
                                  <div className="flex flex-wrap gap-1.5 items-center">
                                    <span className="text-[11px] text-royal/70 font-semibold">Swap with:</span>
                                    {meal.affordable_alternatives.map((alt, ai) => (
                                      <button
                                        key={ai}
                                        type="button"
                                        onClick={() => handleSwapMealWithAlt(activeDayIndex, mk, alt)}
                                        className="px-2.5 py-1 rounded-lg bg-white border border-lavender-border text-[11px] font-bold text-royal hover:bg-royal hover:text-white"
                                      >
                                        {alt.food_name} (₹{alt.cost_inr})
                                      </button>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ) : (
                              <p className="font-bold text-sm text-royal">{meal.food_name}</p>
                            )}

                            <div className="grid grid-cols-5 gap-1.5 text-center text-xs bg-lavender-light p-2 rounded-xl">
                              <div><span className="text-[9px] text-royal/55 block">Calories</span><strong>{Math.round(meal.nutrients.calories_kcal)} kcal</strong></div>
                              <div><span className="text-[9px] text-royal/55 block">Protein</span><strong className="text-lime-dark">{meal.nutrients.protein_g}g</strong></div>
                              <div><span className="text-[9px] text-royal/55 block">Carbs</span><strong>{meal.nutrients.carbs_g}g</strong></div>
                              <div><span className="text-[9px] text-royal/55 block">Fats</span><strong>{meal.nutrients.fat_g}g</strong></div>
                              <div><span className="text-[9px] text-royal/55 block">Fiber</span><strong>{meal.nutrients.fiber_g}g</strong></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: Dynamic Nutritional Summary */}
              {activeTab === 'summary' && (
                <div className="fg-card p-6 space-y-4">
                  <h3 className="font-bold text-base text-royal">
                    Calculated Daily Nutritional Summary (Plan Averages)
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
                    <div className="p-3.5 rounded-xl bg-lavender-light border border-lavender-border">
                      <span className="text-[10px] font-bold uppercase text-royal/55 block">Calories / Day</span>
                      <span className="font-extrabold text-xl text-royal">{avgCalories} kcal</span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-lime-electric/25 border border-lime-electric">
                      <span className="text-[10px] font-bold uppercase text-royal-deep block">Protein / Day</span>
                      <span className="font-extrabold text-xl text-royal-deep">{avgProtein}g</span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-lavender-light border border-lavender-border">
                      <span className="text-[10px] font-bold uppercase text-royal/55 block">Carbs / Day</span>
                      <span className="font-extrabold text-xl text-royal">{avgCarbs}g</span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-lavender-light border border-lavender-border">
                      <span className="text-[10px] font-bold uppercase text-royal/55 block">Fats / Day</span>
                      <span className="font-extrabold text-xl text-royal">{avgFat}g</span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-lavender-light border border-lavender-border">
                      <span className="text-[10px] font-bold uppercase text-royal/55 block">Est. Plan Cost</span>
                      <span className="font-extrabold text-xl text-royal">₹{totalPlanExp}</span>
                    </div>
                  </div>
                  <p className="text-xs text-royal/70">{planData.local_mandi_notes}</p>
                </div>
              )}

              {/* TAB 4: Editable Grocery List */}
              {activeTab === 'grocery' && (
                <div className="fg-card p-5 space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div>
                      <h3 className="font-bold text-base text-royal">
                        {budgetDuration === 'monthly' ? 'Monthly' : 'Weekly'} Grocery List (Editable)
                      </h3>
                      <p className="text-xs text-royal/65">
                        Adjust quantities below to recalculate estimated grocery cost.
                      </p>
                    </div>
                    <span className="font-extrabold text-base text-royal">
                      Total: ₹{totalGroceryCost}
                    </span>
                  </div>

                  <div className="overflow-x-auto rounded-xl border border-lavender-border">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="bg-royal text-white uppercase tracking-wider font-bold">
                          <th className="py-2.5 px-3">Item</th>
                          <th className="py-2.5 px-3">Quantity</th>
                          <th className="py-2.5 px-3 text-right">Unit Price</th>
                          <th className="py-2.5 px-3 text-right">Total Est.</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-lavender-mist">
                        {editableGrocery.map((g, idx) => (
                          <tr key={idx} className="hover:bg-lavender-light">
                            <td className="py-2.5 px-3 font-bold text-royal">{g.name}</td>
                            <td className="py-2.5 px-3">
                              <input
                                type="text"
                                value={g.quantity}
                                onChange={(e) => handleGroceryQtyChange(idx, e.target.value)}
                                className="w-32 px-2.5 py-1 rounded-lg bg-lavender-light border border-lavender-border text-xs font-bold text-royal"
                              />
                            </td>
                            <td className="py-2.5 px-3 text-right text-royal/75">₹{g.unit_price_inr}</td>
                            <td className="py-2.5 px-3 text-right font-bold text-royal">₹{g.total_cost_inr}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
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

export default BudgetPlannerView;
