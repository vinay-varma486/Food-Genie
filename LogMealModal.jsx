import React, { useState, useEffect } from 'react';
import { X, Plus, Search, Loader2, Utensils, ShoppingBag, AlertCircle } from 'lucide-react';
import { apiClient } from './api';
import { useAuth } from './AuthContext';

const MEAL_TYPES = [
  'Breakfast',
  'Morning Snack',
  'Lunch',
  'Evening Snack',
  'Dinner',
  'Grocery Purchase',
];

const DIET_CATEGORIES = [
  { id: 'general_nutrition', label: 'General Nutrition' },
  { id: 'weight_loss', label: 'Weight Loss' },
  { id: 'weight_gain', label: 'Weight Gain' },
  { id: 'muscle_building', label: 'Muscle Building' },
  { id: 'healthy_diet', label: 'Healthy Diet' },
  { id: 'low_budget', label: 'Low Budget Meals' },
  { id: 'high_protein', label: 'High Protein Diet' },
  { id: 'vegetarian', label: 'Vegetarian' },
  { id: 'non_vegetarian', label: 'Non-Vegetarian' },
];

export const LogMealModal = ({
  isOpen,
  onClose,
  onSuccess,
  defaultCategory = 'all',
  sessionId = null,
  initialFood = null,
}) => {
  const { token } = useAuth();
  const [mode, setMode] = useState('catalog'); // 'catalog' | 'custom'
  const [foods, setFoods] = useState([]);
  const [foodSearch, setFoodSearch] = useState('');
  const [selectedFood, setSelectedFood] = useState(null);

  const [entryType, setEntryType] = useState('meal'); // 'meal' | 'purchase'
  const [mealType, setMealType] = useState('Lunch');
  const [dietCategory, setDietCategory] = useState(
    defaultCategory && defaultCategory !== 'all' ? defaultCategory : 'general_nutrition'
  );
  const [servings, setServings] = useState('1');
  const [costInr, setCostInr] = useState('25');

  // Custom entry fields
  const [customName, setCustomName] = useState('');
  const [customCategory, setCustomCategory] = useState('Grains & Millets');
  const [customCalories, setCustomCalories] = useState('');
  const [customProtein, setCustomProtein] = useState('');
  const [customCarbs, setCustomCarbs] = useState('');
  const [customFat, setCustomFat] = useState('');
  const [customFiber, setCustomFiber] = useState('');
  const [customSugar, setCustomSugar] = useState('');

  const [loadingFoods, setLoadingFoods] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setDietCategory(
      defaultCategory && defaultCategory !== 'all' ? defaultCategory : 'general_nutrition'
    );
  }, [defaultCategory]);

  useEffect(() => {
    if (!isOpen) return;
    setError(null);
    if (initialFood) {
      setMode('catalog');
      setSelectedFood(initialFood);
      if (initialFood.estimated_price_inr) {
        setCostInr(String(Math.round(initialFood.estimated_price_inr)));
      }
      if (initialFood.meal_category) {
        setMealType(initialFood.meal_category);
      }
    }
    let active = true;
    async function load() {
      setLoadingFoods(true);
      try {
        const res = await apiClient.getFoodItems('', null, 0, 50);
        if (active && Array.isArray(res)) {
          setFoods(res);
          if (!initialFood && !selectedFood && res.length > 0) {
            setSelectedFood(res[0]);
          }
        }
      } catch (_) {} finally {
        if (active) setLoadingFoods(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [isOpen, initialFood]);

  if (!isOpen) return null;

  const filteredFoods = foods.filter((f) => {
    const q = foodSearch.trim().toLowerCase();
    if (!q) return true;
    return (
      (f.name || '').toLowerCase().includes(q) ||
      (f.category || '').toLowerCase().includes(q) ||
      (f.name_te || '').toLowerCase().includes(q) ||
      (f.name_hi || '').toLowerCase().includes(q)
    );
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;
    setError(null);

    const parsedCost = Number(costInr);
    if (Number.isNaN(parsedCost) || parsedCost < 0) {
      setError('Please enter a valid expense amount (₹0 or greater).');
      return;
    }

    const parsedServings = Number(servings) || 1;
    if (parsedServings <= 0) {
      setError('Servings must be greater than 0.');
      return;
    }

    let payload = {
      entry_type: entryType,
      meal_type: entryType === 'purchase' ? 'Grocery Purchase' : mealType,
      diet_category: dietCategory,
      servings: parsedServings,
      cost_inr: parsedCost,
      session_id: sessionId,
      sugar_g: customSugar !== '' ? Number(customSugar) : null,
    };

    if (mode === 'catalog') {
      if (!selectedFood?.id) {
        setError('Please select a verified food item.');
        return;
      }
      payload.food_id = selectedFood.id;
    } else {
      if (!customName.trim()) {
        setError('Please enter a food or grocery item name.');
        return;
      }
      payload.food_name = customName.trim();
      payload.food_category = customCategory;
      payload.calories_kcal = customCalories !== '' ? Number(customCalories) : 0;
      payload.protein_g = customProtein !== '' ? Number(customProtein) : 0;
      payload.carbs_g = customCarbs !== '' ? Number(customCarbs) : 0;
      payload.fat_g = customFat !== '' ? Number(customFat) : 0;
      payload.fiber_g = customFiber !== '' ? Number(customFiber) : 0;
    }

    setSubmitting(true);
    try {
      await apiClient.createDashboardLog(payload, token);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      setError(err.message || 'Could not save entry. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#230852]/50 backdrop-blur-xs">
      <div className="w-full max-w-lg bg-white rounded-2xl border border-slate-200 shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 bg-[#351078] text-white flex items-center justify-between">
          <div>
            <h3 className="font-display font-bold text-base">Log Meal or Food Purchase</h3>
            <p className="text-xs text-blue-100">
              Updates your real-time calorie, nutrient, and budget analytics
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/10 text-white"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto">
          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Entry Type Toggle: Meal vs Purchase */}
          <div className="grid grid-cols-2 gap-2 p-1 bg-[#FAF7FF] rounded-xl border border-slate-200">
            <button
              type="button"
              onClick={() => setEntryType('meal')}
              className={`py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors ${
                entryType === 'meal' ? 'bg-[#351078] text-white' : 'text-[#5B4B7A]'
              }`}
            >
              <Utensils className="w-3.5 h-3.5" />
              <span>Consumed Meal</span>
            </button>
            <button
              type="button"
              onClick={() => setEntryType('purchase')}
              className={`py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors ${
                entryType === 'purchase' ? 'bg-[#351078] text-white' : 'text-[#5B4B7A]'
              }`}
            >
              <ShoppingBag className="w-3.5 h-3.5" />
              <span>Food Purchase</span>
            </button>
          </div>

          {/* Source Mode Tabs */}
          <div className="flex gap-2 border-b border-slate-200 pb-2">
            <button
              type="button"
              onClick={() => setMode('catalog')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                mode === 'catalog'
                  ? 'bg-[#EEF8FC] text-[#351078] border border-[#ADD8E6]'
                  : 'text-[#5B4B7A] hover:text-[#230852]'
              }`}
            >
              Verified Nutrition DB ({foods.length})
            </button>
            <button
              type="button"
              onClick={() => setMode('custom')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                mode === 'custom'
                  ? 'bg-[#EEF8FC] text-[#351078] border border-[#ADD8E6]'
                  : 'text-[#5B4B7A] hover:text-[#230852]'
              }`}
            >
              Custom Item
            </button>
          </div>

          {mode === 'catalog' ? (
            <div className="space-y-3">
              <div className="relative">
                <Search className="w-4 h-4 text-[#5B4B7A] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={foodSearch}
                  onChange={(e) => setFoodSearch(e.target.value)}
                  placeholder="Search spinach, ragi, paneer, eggs..."
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs sm:text-sm text-[#230852] focus:outline-none focus:border-[#351078]"
                />
              </div>

              <div className="max-h-40 overflow-y-auto border border-slate-200 rounded-xl divide-y divide-slate-100">
                {loadingFoods ? (
                  <div className="p-4 flex items-center justify-center gap-2 text-xs text-[#5B4B7A]">
                    <Loader2 className="w-4 h-4 animate-spin text-[#351078]" />
                    <span>Loading verified foods...</span>
                  </div>
                ) : filteredFoods.length === 0 ? (
                  <p className="p-4 text-xs text-[#5B4B7A] text-center">No matching foods found.</p>
                ) : (
                  filteredFoods.slice(0, 25).map((f) => {
                    const active = selectedFood?.id === f.id;
                    return (
                      <button
                        key={f.id}
                        type="button"
                        onClick={() => setSelectedFood(f)}
                        className={`w-full px-3.5 py-2 text-left flex items-center justify-between gap-2 text-xs transition-colors ${
                          active ? 'bg-[#EEF8FC] text-[#351078] font-bold' : 'hover:bg-slate-50 text-[#230852]'
                        }`}
                      >
                        <div className="min-w-0">
                          <p className="truncate">{f.name}</p>
                          <p className="text-[10px] text-[#5B4B7A] capitalize">{f.category}</p>
                        </div>
                        <span className="text-[11px] font-bold text-[#351078] flex-shrink-0">
                          {Math.round(f.calories_kcal)} kcal • {f.protein_g}g P /100g
                        </span>
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
                    Food / Item Name *
                  </label>
                  <input
                    type="text"
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    placeholder="e.g., Dal Tadka Bowl"
                    className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs text-[#230852] focus:outline-none focus:border-[#351078]"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
                    Food Group
                  </label>
                  <select
                    value={customCategory}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs text-[#230852] focus:outline-none focus:border-[#351078]"
                  >
                    <option>Grains &amp; Millets</option>
                    <option>Pulses &amp; Proteins</option>
                    <option>Greens &amp; Vegetables</option>
                    <option>Fruits</option>
                    <option>Dairy &amp; Eggs</option>
                    <option>Seeds &amp; Nuts</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                {[
                  { label: 'kcal', val: customCalories, set: setCustomCalories },
                  { label: 'Protein(g)', val: customProtein, set: setCustomProtein },
                  { label: 'Carbs(g)', val: customCarbs, set: setCustomCarbs },
                  { label: 'Fat(g)', val: customFat, set: setCustomFat },
                  { label: 'Fiber(g)', val: customFiber, set: setCustomFiber },
                  { label: 'Sugar(g)', val: customSugar, set: setCustomSugar },
                ].map((m) => (
                  <div key={m.label}>
                    <label className="block text-[10px] font-bold text-[#5B4B7A] mb-1">{m.label}</label>
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      value={m.val}
                      onChange={(e) => m.set(e.target.value)}
                      placeholder="0"
                      className="w-full px-2 py-1.5 rounded-lg bg-[#FAF7FF] border border-slate-200 text-xs text-[#230852]"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Shared Controls: Meal Type, Category, Servings, Expense ₹ */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
            <div>
              <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
                Meal Slot
              </label>
              <select
                value={mealType}
                onChange={(e) => setMealType(e.target.value)}
                disabled={entryType === 'purchase'}
                className="w-full px-2.5 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs font-semibold text-[#230852]"
              >
                {MEAL_TYPES.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
                Servings
              </label>
              <input
                type="number"
                min="0.25"
                step="0.25"
                value={servings}
                onChange={(e) => setServings(e.target.value)}
                className="w-full px-2.5 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs font-bold text-[#230852]"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
                Cost (₹ INR)
              </label>
              <input
                type="number"
                min="0"
                step="1"
                value={costInr}
                onChange={(e) => setCostInr(e.target.value)}
                className="w-full px-2.5 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs font-bold text-[#230852]"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
                Diet Goal Tag
              </label>
              <select
                value={dietCategory}
                onChange={(e) => setDietCategory(e.target.value)}
                className="w-full px-2.5 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs font-semibold text-[#230852]"
              >
                {DIET_CATEGORIES.map((c) => (
                  <option key={c.id} value={c.id}>{c.label}</option>
                ))}
              </select>
            </div>
          </div>

          {mode === 'catalog' && (
            <div>
              <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
                Optional Sugar (g) — Only if known on package label
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={customSugar}
                onChange={(e) => setCustomSugar(e.target.value)}
                placeholder="Leave blank if unavailable (never guessed)"
                className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-xs text-[#230852]"
              />
            </div>
          )}

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-bold text-[#5B4B7A] hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded-xl bg-[#351078] hover:bg-[#351078] text-white text-xs font-bold flex items-center gap-1.5 disabled:opacity-50"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              <span>{submitting ? 'Saving...' : 'Save to Dashboard'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LogMealModal;

