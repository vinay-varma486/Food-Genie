import React, { useState, useEffect, useCallback } from 'react';
import {
  ShoppingBag,
  CheckSquare,
  Square,
  RefreshCw,
  Plus,
  Loader2,
  AlertCircle,
  Tag,
} from 'lucide-react';
import { apiClient } from './api';
import { useAuth } from './AuthContext';

export const ShoppingListView = ({ sessionId, onLoggedPurchase }) => {
  const { token } = useAuth();
  const [weeklyBudget, setWeeklyBudget] = useState('1000');
  const [familyMembers, setFamilyMembers] = useState('1');
  const [dietaryPref, setDietaryPref] = useState('vegetarian');

  const [basket, setBasket] = useState(null);
  const [catalogItems, setCatalogItems] = useState([]);
  const [checkedNames, setCheckedNames] = useState({});
  const [loading, setLoading] = useState(true);
  const [loggingItem, setLoggingItem] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  const loadShoppingData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [basketRes, itemsRes] = await Promise.all([
        apiClient.buildGroceryBasket({
          weekly_budget_inr: Number(weeklyBudget) || 1000,
          family_members: Number(familyMembers) || 1,
          dietary_preference: dietaryPref,
          language: 'en',
        }),
        apiClient.getGroceryItems(),
      ]);
      setBasket(basketRes);
      setCatalogItems(Array.isArray(itemsRes) ? itemsRes : []);
    } catch (err) {
      setError(err.message || 'Unable to load shopping list right now.');
    } finally {
      setLoading(false);
    }
  }, [weeklyBudget, familyMembers, dietaryPref]);

  useEffect(() => {
    loadShoppingData();
  }, [loadShoppingData]);

  const toggleCheck = (name) => {
    setCheckedNames((prev) => ({ ...prev, [name]: !prev[name] }));
  };

  const handleLogPurchase = async (itemName, category, costInr) => {
    if (loggingItem) return;
    setLoggingItem(itemName);
    setFeedback(null);
    setError(null);
    try {
      await apiClient.createDashboardLog(
        {
          food_name: itemName,
          food_category: category || 'Groceries',
          meal_type: 'Grocery Purchase',
          entry_type: 'purchase',
          cost_inr: Number(costInr) || 0,
          servings: 1,
          session_id: sessionId,
        },
        token
      );
      setCheckedNames((prev) => ({ ...prev, [itemName]: true }));
      setFeedback(`Recorded grocery purchase "${itemName}" (₹${Math.round(costInr)}) in Budget Analytics.`);
      if (onLoggedPurchase) onLoggedPurchase();
    } catch (err) {
      setError(err.message || 'Could not log grocery purchase.');
    } finally {
      setLoggingItem(null);
    }
  };

  const basketItems = basket?.items || basket?.recommended_basket || [];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-display font-extrabold text-2xl text-[#230852] flex items-center gap-2.5">
            <ShoppingBag className="w-6 h-6 text-[#351078]" />
            <span>Smart Shopping List</span>
          </h1>
          <p className="text-xs sm:text-sm text-[#5B4B7A] mt-0.5">
            Cost-optimized Indian wholefoods &amp; mandi benchmark pricing with one-click expense logging
          </p>
        </div>

        <button
          type="button"
          onClick={loadShoppingData}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-[#351078] hover:bg-[#351078] text-white text-xs font-bold flex items-center gap-1.5 self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Optimize Basket</span>
        </button>
      </div>

      {/* Controls */}
      <div className="fg-card p-5 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
            Weekly Grocery Budget (₹)
          </label>
          <input
            type="number"
            min="200"
            step="50"
            value={weeklyBudget}
            onChange={(e) => setWeeklyBudget(e.target.value)}
            className="w-full px-3.5 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-sm font-bold text-[#230852]"
          />
        </div>
        <div>
          <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
            Household Size
          </label>
          <select
            value={familyMembers}
            onChange={(e) => setFamilyMembers(e.target.value)}
            className="w-full px-3.5 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-sm font-bold text-[#230852]"
          >
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <option key={n} value={n}>{n} {n === 1 ? 'Person' : 'People'}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
            Dietary Style
          </label>
          <select
            value={dietaryPref}
            onChange={(e) => setDietaryPref(e.target.value)}
            className="w-full px-3.5 py-2 rounded-xl bg-[#FAF7FF] border border-slate-200 text-sm font-bold text-[#230852]"
          >
            <option value="vegetarian">Vegetarian</option>
            <option value="non-vegetarian">Non-Vegetarian</option>
            <option value="vegan">Vegan</option>
          </select>
        </div>
      </div>

      {feedback && (
        <div className="p-3 rounded-xl bg-green-50 border border-green-200 text-xs font-bold text-[#16A34A]">
          {feedback}
        </div>
      )}
      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="py-12 flex items-center justify-center gap-2 text-xs font-bold text-[#351078]">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Calculating cost-optimized shopping list...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Optimized Weekly Basket */}
          <div className="lg:col-span-7 fg-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h2 className="font-bold text-base text-[#230852]">Weekly Optimized Basket</h2>
                <p className="text-xs text-[#5B4B7A]">
                  Est. Total: <strong className="text-[#351078]">₹{Math.round(basket?.total_estimated_cost_inr || 0)}</strong>
                </p>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-[#EEF8FC] text-[#351078] text-xs font-bold">
                {basketItems.length} Staples
              </span>
            </div>

            {basketItems.length === 0 ? (
              <p className="text-xs text-[#5B4B7A] py-6 text-center">No basket items returned.</p>
            ) : (
              <div className="space-y-2.5">
                {basketItems.map((item, idx) => {
                  const name = item.item_name || item.name;
                  const checked = Boolean(checkedNames[name]);
                  const cost = item.estimated_cost_inr ?? item.avg_price_inr ?? 0;
                  return (
                    <div
                      key={`${name}-${idx}`}
                      className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 transition-colors ${
                        checked ? 'bg-slate-50 border-slate-200 opacity-75' : 'bg-[#FAF7FF] border-slate-200'
                      }`}
                    >
                      <button
                        type="button"
                        onClick={() => toggleCheck(name)}
                        className="flex items-start gap-3 text-left min-w-0 flex-1"
                      >
                        {checked ? (
                          <CheckSquare className="w-4 h-4 text-[#16A34A] flex-shrink-0 mt-0.5" />
                        ) : (
                          <Square className="w-4 h-4 text-[#351078] flex-shrink-0 mt-0.5" />
                        )}
                        <div className="min-w-0">
                          <p className={`text-xs sm:text-sm font-bold text-[#230852] ${checked ? 'line-through' : ''}`}>
                            {name}
                          </p>
                          <p className="text-[11px] text-[#5B4B7A]">
                            {item.quantity || item.standard_quantity || '1 unit'} • {item.category || 'Staple'}
                          </p>
                        </div>
                      </button>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="text-xs font-extrabold text-[#230852]">₹{Math.round(cost)}</span>
                        <button
                          type="button"
                          onClick={() => handleLogPurchase(name, item.category, cost)}
                          disabled={loggingItem === name}
                          className="px-2.5 py-1.5 rounded-lg bg-[#EEF8FC] hover:bg-[#351078] text-[#351078] hover:text-white text-[11px] font-bold border border-[#ADD8E6] flex items-center gap-1 transition-colors"
                          title="Record as Food Purchase in Dashboard"
                        >
                          <Plus className="w-3 h-3" />
                          <span>{loggingItem === name ? '...' : 'Log Buy'}</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Regional Budget Hero Reference Staples */}
          <div className="lg:col-span-5 fg-card p-5 space-y-4">
            <div className="border-b border-slate-100 pb-3">
              <h2 className="font-bold text-base text-[#230852] flex items-center gap-2">
                <Tag className="w-4 h-4 text-[#16A34A]" />
                <span>Verified Mandi Staples &amp; Swaps</span>
              </h2>
              <p className="text-xs text-[#5B4B7A]">Database grocery reference prices</p>
            </div>

            <div className="space-y-2.5">
              {catalogItems.map((g) => (
                <div
                  key={g.id}
                  className="p-3 rounded-xl bg-[#FAF7FF] border border-slate-200 space-y-1"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold text-[#230852]">{g.name}</span>
                    <span className="text-xs font-extrabold text-[#351078]">
                      ₹{Math.round(g.avg_price_inr)} / {g.standard_quantity}
                    </span>
                  </div>
                  {g.affordable_substitute_for && (
                    <p className="text-[11px] text-[#16A34A] font-semibold">
                      Smart Swap: {g.affordable_substitute_for}
                    </p>
                  )}
                  {g.nutritional_perks && (
                    <p className="text-[11px] text-[#5B4B7A]">{g.nutritional_perks}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShoppingListView;

