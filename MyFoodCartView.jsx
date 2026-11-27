import React, { useState, useEffect } from 'react';
import {
  ShoppingCart,
  Download,
  Trash2,
  Plus,
  Minus,
  Bookmark,
  Check,
  Edit2,
  Loader2,
  AlertCircle,
  LogIn,
  Sparkles,
  Flame,
  Wallet,
} from 'lucide-react';
import { useAuth } from './AuthContext';
import { apiClient } from './api';

const MEAL_TABS = [
  { id: 'all', label: 'All Meals' },
  { id: 'Breakfast', label: 'Breakfast' },
  { id: 'Morning Snack', label: 'Morning Snack' },
  { id: 'Lunch', label: 'Lunch' },
  { id: 'Evening Snacks', label: 'Evening Snacks' },
  { id: 'Dinner', label: 'Dinner' },
];

export const MyFoodCartView = ({
  cart,
  loading = false,
  onRefreshCart,
  onCartUpdated,
  onOpenAuth,
  onAskGenie,
  onBrowseFoods,
}) => {
  const { token, isAuthenticated } = useAuth();
  const [activeMealTab, setActiveMealTab] = useState('all');
  const [editingItemId, setEditingItemId] = useState(null);
  const [editNotes, setEditNotes] = useState('');
  const [editMealSlot, setEditMealSlot] = useState('Lunch');
  const [editFoodName, setEditFoodName] = useState('');

  const [catalogFoods, setCatalogFoods] = useState([]);
  const [quickFoodId, setQuickFoodId] = useState('');
  const [quickSlot, setQuickSlot] = useState('Breakfast');
  const [addingQuick, setAddingQuick] = useState(false);

  const [savingCart, setSavingCart] = useState(false);
  const [saveAsPlan, setSaveAsPlan] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    async function loadCatalog() {
      try {
        const list = await apiClient.getFoodItems('', null, 0, 40);
        if (active && Array.isArray(list)) {
          setCatalogFoods(list);
          if (list.length > 0 && !quickFoodId) {
            setQuickFoodId(String(list[0].id));
          }
        }
      } catch (_) {}
    }
    loadCatalog();
    return () => {
      active = false;
    };
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
        <div className="fg-card p-8 sm:p-10 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-[#351078] text-[#C6FF00] flex items-center justify-center mx-auto">
            <ShoppingCart className="w-7 h-7" />
          </div>
          <h1 className="font-display font-extrabold text-2xl text-[#351078]">
            My Food Cart
          </h1>
          <p className="text-sm text-[#5B4B7A] max-w-md mx-auto leading-relaxed">
            Sign in or create a verified FoodGenie account to save recommended foods to your personal cart, organize daily meals, persist your selections across logins, and download printable nutrition PDFs.
          </p>
          <button
            type="button"
            onClick={onOpenAuth}
            className="px-6 py-3 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold inline-flex items-center gap-2 shadow-card transition-colors"
          >
            <LogIn className="w-4 h-4 text-[#C6FF00]" />
            <span>Sign In / Register to Use Food Cart</span>
          </button>
        </div>
      </div>
    );
  }

  const items = cart?.items || [];
  const totals = cart?.totals || {
    total_items: 0,
    total_calories: 0,
    total_protein_g: 0,
    total_carbs_g: 0,
    total_fat_g: 0,
    total_fiber_g: 0,
    total_estimated_cost_inr: 0,
    daily_calorie_target: 2000,
    daily_budget_inr: 166.67,
    calorie_target_percent: 0,
  };

  const filteredItems =
    activeMealTab === 'all'
      ? items
      : items.filter((i) => i.meal_category === activeMealTab);

  const handleQtyDelta = async (item, delta) => {
    const nextQty = Math.round((Number(item.quantity) + delta) * 4) / 4;
    setError(null);
    setFeedback(null);
    try {
      const updated =
        nextQty <= 0
          ? await apiClient.removeCartItem(item.id, token)
          : await apiClient.updateCartItem(item.id, { quantity: nextQty }, token);
      if (onCartUpdated) onCartUpdated(updated);
    } catch (err) {
      setError(err.message || 'Could not update quantity.');
    }
  };

  const handleStartEdit = (item) => {
    setEditingItemId(item.id);
    setEditFoodName(item.food_name);
    setEditMealSlot(item.meal_category || 'Lunch');
    setEditNotes(item.notes || '');
  };

  const handleSaveEdit = async (itemId) => {
    setError(null);
    try {
      const updated = await apiClient.updateCartItem(
        itemId,
        {
          food_name: editFoodName.trim(),
          meal_category: editMealSlot,
          notes: editNotes,
        },
        token
      );
      if (onCartUpdated) onCartUpdated(updated);
      setEditingItemId(null);
      setFeedback('Updated cart item details.');
    } catch (err) {
      setError(err.message || 'Could not update cart item.');
    }
  };

  const handleRemove = async (itemId) => {
    setError(null);
    try {
      const updated = await apiClient.removeCartItem(itemId, token);
      if (onCartUpdated) onCartUpdated(updated);
    } catch (err) {
      setError(err.message || 'Could not remove item.');
    }
  };

  const handleQuickAdd = async (e) => {
    e.preventDefault();
    if (!quickFoodId || addingQuick) return;
    setAddingQuick(true);
    setError(null);
    setFeedback(null);
    try {
      const updated = await apiClient.addToCart(
        { food_id: Number(quickFoodId), meal_category: quickSlot, quantity: 1 },
        token
      );
      if (onCartUpdated) onCartUpdated(updated);
      setFeedback('Added food to My Food Cart.');
    } catch (err) {
      setError(err.message || 'Could not add food to cart.');
    } finally {
      setAddingQuick(false);
    }
  };

  const handleSaveCart = async () => {
    if (savingCart) return;
    setSavingCart(true);
    setError(null);
    setFeedback(null);
    try {
      const res = await apiClient.saveCart(
        { title: cart?.title || 'My Food Cart', save_as_meal_plan: saveAsPlan },
        token
      );
      if (res?.cart && onCartUpdated) onCartUpdated(res.cart);
      setFeedback(
        res?.saved_plan_id
          ? 'Food Cart saved to your account and stored under Saved Meal Plans!'
          : 'Food Cart saved to your account.'
      );
    } catch (err) {
      setError(err.message || 'Could not save cart.');
    } finally {
      setSavingCart(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (downloadingPdf) return;
    setDownloadingPdf(true);
    setError(null);
    try {
      const blob = await apiClient.downloadCartPdf(token);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'foodgenie-food-cart.pdf';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setFeedback('Downloaded your FoodGenie Food Cart PDF!');
    } catch (err) {
      setError(err.message || 'PDF download failed.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-6xl mx-auto">
      {/* Header & Main Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#EEF8FC] border border-[#ADD8E6] text-[#351078] text-[11px] font-bold mb-1">
            <ShoppingCart className="w-3.5 h-3.5" />
            <span>Saved Account Meal Cart</span>
          </div>
          <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-[#351078]">
            My Food Cart
          </h1>
          <p className="text-xs sm:text-sm text-[#5B4B7A]">
            Organize recommended foods across meals, monitor calories &amp; ₹ budget, and export as PDF
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {onAskGenie && (
            <button
              type="button"
              onClick={() => onAskGenie('Analyze my Food Cart for calorie/protein balance and suggest cheaper swaps if needed.')}
              className="px-3.5 py-2.5 rounded-xl bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#230852] text-xs font-bold border border-[#ADD8E6] flex items-center gap-1.5 transition-colors"
            >
              <Sparkles className="w-4 h-4 text-[#351078]" />
              <span>Ask Genie About Cart</span>
            </button>
          )}

          <button
            type="button"
            onClick={handleSaveCart}
            disabled={savingCart || items.length === 0}
            className="px-4 py-2.5 rounded-xl bg-white hover:bg-[#F2ECFF] text-[#351078] text-xs font-bold border border-[#D8C5FF] flex items-center gap-1.5 disabled:opacity-50 transition-colors"
          >
            {savingCart ? <Loader2 className="w-4 h-4 animate-spin" /> : <Bookmark className="w-4 h-4" />}
            <span>{savingCart ? 'Saving...' : 'Save Cart'}</span>
          </button>

          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={downloadingPdf || items.length === 0}
            className="px-4 py-2.5 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center gap-1.5 shadow-card disabled:opacity-50 transition-colors"
          >
            {downloadingPdf ? (
              <Loader2 className="w-4 h-4 animate-spin text-[#C6FF00]" />
            ) : (
              <Download className="w-4 h-4 text-[#C6FF00]" />
            )}
            <span>{downloadingPdf ? 'Generating PDF...' : 'Download PDF'}</span>
          </button>
        </div>
      </div>

      {/* 5 Totals Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        {[
          {
            label: 'Total Calories',
            value: `${Math.round(totals.total_calories)} kcal`,
            sub: `${totals.calorie_target_percent}% of ${totals.daily_calorie_target} goal`,
            icon: Flame,
          },
          { label: 'Total Protein', value: `${totals.total_protein_g} g`, sub: 'Bioavailable total' },
          { label: 'Total Carbs', value: `${totals.total_carbs_g} g`, sub: 'Energy carbs' },
          { label: 'Total Fats', value: `${totals.total_fat_g} g`, sub: `Fiber: ${totals.total_fiber_g}g` },
          {
            label: 'Total Est. Cost',
            value: `₹${Number(totals.total_estimated_cost_inr || 0).toLocaleString()}`,
            sub: `Daily budget ref: ₹${Math.round(totals.daily_budget_inr)}`,
            icon: Wallet,
            highlight: true,
          },
        ].map((card) => (
          <div
            key={card.label}
            className={`fg-card p-4 space-y-1 ${card.highlight ? 'bg-[#EEF8FC] border-[#ADD8E6]' : ''}`}
          >
            <p className="text-[11px] font-bold text-[#5B4B7A]">{card.label}</p>
            <p className="font-display font-extrabold text-xl text-[#230852]">{card.value}</p>
            <p className="text-[11px] font-semibold text-[#351078]">{card.sub}</p>
          </div>
        ))}
      </div>

      {/* Quick Add Item Bar */}
      <form onSubmit={handleQuickAdd} className="fg-card p-4 flex flex-col sm:flex-row items-stretch sm:items-end gap-3">
        <div className="flex-1">
          <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
            Quick Add Verified Food
          </label>
          <select
            value={quickFoodId}
            onChange={(e) => setQuickFoodId(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs sm:text-sm font-semibold text-[#230852]"
          >
            {catalogFoods.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({Math.round(f.calories_kcal)} kcal / {f.protein_g}g P per 100g)
              </option>
            ))}
          </select>
        </div>

        <div className="sm:w-44">
          <label className="block text-[11px] font-bold uppercase text-[#5B4B7A] mb-1">
            Meal Slot
          </label>
          <select
            value={quickSlot}
            onChange={(e) => setQuickSlot(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-[#FAF7FF] border border-[#D8C5FF] text-xs font-bold text-[#230852]"
          >
            {MEAL_TABS.filter((t) => t.id !== 'all').map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={addingQuick || !quickFoodId}
          className="px-4 py-2.5 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center justify-center gap-1.5"
        >
          <Plus className="w-4 h-4 text-[#C6FF00]" />
          <span>{addingQuick ? 'Adding...' : 'Add Item'}</span>
        </button>
      </form>

      {/* Optional Snapshot Save Toggle */}
      <label className="flex items-center gap-2 text-xs font-semibold text-[#5B4B7A] cursor-pointer px-1">
        <input
          type="checkbox"
          checked={saveAsPlan}
          onChange={(e) => setSaveAsPlan(e.target.checked)}
          className="rounded accent-[#351078]"
        />
        <span>When clicking &quot;Save Cart&quot;, also archive a snapshot under Saved Meal Plans</span>
      </label>

      {feedback && (
        <div className="p-3 rounded-xl bg-green-50 border border-green-200 text-xs font-bold text-[#16A34A] flex items-center gap-2">
          <Check className="w-4 h-4 flex-shrink-0" />
          <span>{feedback}</span>
        </div>
      )}
      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Meal Slot Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {MEAL_TABS.map((t) => {
          const count =
            t.id === 'all'
              ? items.length
              : items.filter((i) => i.meal_category === t.id).length;
          const active = activeMealTab === t.id;
          return (
            <button
              key={t.id}
              type="button"
              onClick={() => setActiveMealTab(t.id)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap border transition-colors ${
                active
                  ? 'bg-[#351078] text-white border-[#351078]'
                  : 'bg-white text-[#230852] border-[#D8C5FF] hover:bg-[#FAF7FF]'
              }`}
            >
              {t.label} ({count})
            </button>
          );
        })}
      </div>

      {/* Cart Items List */}
      {loading && items.length === 0 ? (
        <div className="py-12 flex items-center justify-center gap-2 text-xs font-bold text-[#351078]">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading your Food Cart...</span>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="fg-card p-10 text-center space-y-3">
          <p className="font-bold text-base text-[#230852]">
            {items.length === 0 ? 'Your Food Cart is empty' : `No foods assigned to ${activeMealTab}`}
          </p>
          <p className="text-xs text-[#5B4B7A] max-w-md mx-auto">
            Click &quot;Add to My Food Cart&quot; on any recommended food from Genie AI, Dashboard, or Food Categories.
          </p>
          {onBrowseFoods && (
            <button
              type="button"
              onClick={onBrowseFoods}
              className="px-4 py-2 rounded-xl bg-[#351078] text-white text-xs font-bold"
            >
              Explore Verified Foods
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredItems.map((item) => {
            const isEditing = editingItemId === item.id;
            return (
              <div
                key={item.id}
                className="fg-card p-4 sm:p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4"
              >
                <div className="flex items-start gap-3.5 min-w-0 flex-1">
                  {item.image_url && (
                    <img
                      src={item.image_url}
                      alt={item.food_name}
                      className="w-16 h-16 rounded-xl object-cover border border-[#E5DAFB] flex-shrink-0 hidden sm:block"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  )}

                  <div className="min-w-0 flex-1 space-y-1.5">
                    {isEditing ? (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <input
                          type="text"
                          value={editFoodName}
                          onChange={(e) => setEditFoodName(e.target.value)}
                          className="px-2.5 py-1.5 rounded-lg bg-[#FAF7FF] border border-[#D8C5FF] text-xs font-bold text-[#230852]"
                        />
                        <select
                          value={editMealSlot}
                          onChange={(e) => setEditMealSlot(e.target.value)}
                          className="px-2.5 py-1.5 rounded-lg bg-[#FAF7FF] border border-[#D8C5FF] text-xs font-bold text-[#230852]"
                        >
                          {MEAL_TABS.filter((t) => t.id !== 'all').map((t) => (
                            <option key={t.id} value={t.id}>{t.label}</option>
                          ))}
                        </select>
                        <input
                          type="text"
                          value={editNotes}
                          onChange={(e) => setEditNotes(e.target.value)}
                          placeholder="Preparation note..."
                          className="px-2.5 py-1.5 rounded-lg bg-[#FAF7FF] border border-[#D8C5FF] text-xs text-[#230852]"
                        />
                      </div>
                    ) : (
                      <>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="px-2.5 py-0.5 rounded-full bg-[#EEF8FC] border border-[#ADD8E6] text-[#351078] text-[10px] font-extrabold uppercase">
                            {item.meal_category}
                          </span>
                          <span className="text-[11px] font-semibold text-[#5B4B7A]">
                            {item.serving_size} per unit
                          </span>
                        </div>
                        <h3 className="font-display font-bold text-base text-[#230852]">
                          {item.food_name}
                        </h3>
                        {item.health_benefits && (
                          <p className="text-xs text-[#5B4B7A] line-clamp-2">{item.health_benefits}</p>
                        )}
                        {(item.vitamins_summary?.length > 0 || item.minerals_summary?.length > 0) && (
                          <div className="flex flex-wrap gap-1 pt-0.5">
                            {[...(item.vitamins_summary || []).slice(0, 2), ...(item.minerals_summary || []).slice(0, 2)].map((n) => (
                              <span
                                key={n}
                                className="px-2 py-0.5 rounded-md bg-[#F2ECFF] text-[#351078] text-[10px] font-semibold"
                              >
                                {n}
                              </span>
                            ))}
                          </div>
                        )}
                        {item.notes && (
                          <p className="text-[11px] italic text-[#351078]">Note: {item.notes}</p>
                        )}
                      </>
                    )}
                  </div>
                </div>

                {/* Right: Totals + Stepper + Edit/Delete */}
                <div className="flex flex-wrap sm:flex-nowrap items-center justify-between lg:justify-end gap-4 border-t lg:border-t-0 pt-3 lg:pt-0 border-[#F2ECFF]">
                  <div className="grid grid-cols-4 gap-2 text-center text-[11px]">
                    <div className="px-2 py-1 rounded-lg bg-[#FAF7FF] border border-[#E5DAFB]">
                      <span className="block text-[9px] text-[#5B4B7A] font-bold">Kcal</span>
                      <strong className="text-[#230852]">{Math.round(item.total_calories)}</strong>
                    </div>
                    <div className="px-2 py-1 rounded-lg bg-[#EEF8FC] border border-[#ADD8E6]">
                      <span className="block text-[9px] text-[#351078] font-bold">Prot</span>
                      <strong className="text-[#230852]">{item.total_protein_g}g</strong>
                    </div>
                    <div className="px-2 py-1 rounded-lg bg-[#FAF7FF] border border-[#E5DAFB]">
                      <span className="block text-[9px] text-[#5B4B7A] font-bold">Carbs</span>
                      <strong className="text-[#230852]">{item.total_carbs_g}g</strong>
                    </div>
                    <div className="px-2 py-1 rounded-lg bg-[#FAF7FF] border border-[#E5DAFB]">
                      <span className="block text-[9px] text-[#5B4B7A] font-bold">Fat</span>
                      <strong className="text-[#230852]">{item.total_fat_g}g</strong>
                    </div>
                  </div>

                  {/* Quantity Stepper */}
                  <div className="inline-flex items-center rounded-xl border border-[#D8C5FF] bg-[#FAF7FF] overflow-hidden">
                    <button
                      type="button"
                      onClick={() => handleQtyDelta(item, -1)}
                      className="p-2 hover:bg-[#E5DAFB] text-[#351078]"
                      title="Decrease quantity"
                    >
                      <Minus className="w-3.5 h-3.5" />
                    </button>
                    <span className="px-3 text-xs font-extrabold text-[#230852]">
                      {item.quantity}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleQtyDelta(item, 1)}
                      className="p-2 hover:bg-[#E5DAFB] text-[#351078]"
                      title="Increase quantity"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="text-right min-w-[68px]">
                    <p className="font-display font-extrabold text-base text-[#351078]">
                      ₹{Number(item.total_estimated_cost_inr || 0).toFixed(0)}
                    </p>
                    <p className="text-[10px] text-[#5B4B7A]">est. total</p>
                  </div>

                  <div className="flex items-center gap-1">
                    {isEditing ? (
                      <button
                        type="button"
                        onClick={() => handleSaveEdit(item.id)}
                        className="px-2.5 py-1.5 rounded-lg bg-[#351078] text-white text-xs font-bold"
                      >
                        Save
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleStartEdit(item)}
                        className="p-2 rounded-lg text-[#5B4B7A] hover:text-[#351078] hover:bg-[#F2ECFF]"
                        title="Edit meal slot or note"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleRemove(item.id)}
                      className="p-2 rounded-lg text-[#5B4B7A] hover:text-red-600 hover:bg-red-50"
                      title="Remove item"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MyFoodCartView;

