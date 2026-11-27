import React, { useState } from 'react';
import {
  Wallet,
  CreditCard,
  PiggyBank,
  Flame,
  Sparkles,
  Lightbulb,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Info,
  Trash2,
  Plus,
  Stethoscope,
  Utensils,
  MessageSquare,
  RotateCcw,
} from 'lucide-react';
import { BudgetAnalyticsSection } from './BudgetAnalyticsSection';
import { NutritionAnalyticsSection } from './NutritionAnalyticsSection';
import { FoodCardDetailed } from './FoodCardDetailed';

const KPI_ICONS = {
  budget: Wallet,
  spent: CreditCard,
  remaining: PiggyBank,
  calories: Flame,
};

export const DashboardView = ({
  overview,
  loading = false,
  error = null,
  selectedCategory = 'all',
  onSelectCategory,
  onSetGuestBudget,
  onOpenLogModal,
  onLogSpecificFood,
  onAddToCart,
  cartFoodIds = new Set(),
  onApplyCategoryPlan,
  applyingPlan = false,
  onDeleteLog,
  onAskGenie,
  onNavigate,
  onRetry,
}) => {
  const [editingBudget, setEditingBudget] = useState(false);
  const [budgetDraft, setBudgetDraft] = useState('4500');
  const [quickGenieQuery, setQuickGenieQuery] = useState('');

  if (loading && !overview) {
    return (
      <div className="p-8 space-y-6 animate-pulse">
        <div className="h-12 bg-white rounded-2xl border border-[#D8C5FF]" />
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-white rounded-2xl border border-[#D8C5FF]" />
          ))}
        </div>
        <div className="h-80 bg-white rounded-2xl border border-[#D8C5FF]" />
      </div>
    );
  }

  if (error && !overview) {
    return (
      <div className="p-8">
        <div className="fg-card p-6 text-center space-y-3 max-w-lg mx-auto">
          <AlertTriangle className="w-8 h-8 text-[#F59E0B] mx-auto" />
          <h2 className="font-bold text-base text-[#230852]">Unable to load dashboard analytics</h2>
          <p className="text-xs text-[#5B4B7A]">{error}</p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="px-4 py-2 rounded-xl bg-[#351078] text-white text-xs font-bold inline-flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[#C6FF00]" />
              <span>Retry</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!overview) return null;

  const categories = overview.categories_catalog || [];
  const activeCat = overview.active_category_info || {};
  const recommendedFoods = overview.category_recommended_foods || [];
  const suggestedMeals = overview.category_suggested_meals || [];
  const insights = overview.smart_insights || [];
  const recentActivity = overview.recent_activity || [];
  const foodLogs = overview.food_logs || [];

  const kpiCards = [
    { key: 'budget', metric: overview.total_budget_card, canEditBudget: true },
    { key: 'spent', metric: overview.total_spent_card },
    { key: 'remaining', metric: overview.remaining_budget_card },
    { key: 'calories', metric: overview.total_calories_card },
  ];

  const handleBudgetSubmit = (e) => {
    e.preventDefault();
    const val = Number(budgetDraft);
    if (val > 0 && onSetGuestBudget) {
      onSetGuestBudget(val);
      setEditingBudget(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-7 max-w-[1440px] mx-auto">
      {/* 1. Prominent Category-Based Dashboard Selector */}
      <section className="fg-card p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <p className="text-[11px] font-extrabold uppercase tracking-wider text-[#351078]">
              Category-Based Dashboard Filter
            </p>
            <p className="text-xs text-[#5B4B7A]">
              Select a nutrition goal or diet category to update recommended foods, nutrient targets, meals, and charts
            </p>
          </div>
          {selectedCategory !== 'all' && (
            <button
              type="button"
              onClick={() => onSelectCategory && onSelectCategory('all')}
              className="px-3 py-1 rounded-lg bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#351078] text-xs font-bold border border-[#ADD8E6] self-start sm:self-auto"
            >
              Reset to All Categories
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {categories.map((cat) => {
            const active = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => onSelectCategory && onSelectCategory(cat.id)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap border transition-all duration-150 ${
                  active
                    ? 'bg-[#351078] text-white border-[#351078] shadow-xs'
                    : 'bg-[#F2ECFF]/60 hover:bg-[#EEF8FC] text-[#230852] border-[#D8C5FF] hover:border-[#ADD8E6]'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </section>

      {/* 2. Four Summary KPI Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {kpiCards.map(({ key, metric, canEditBudget }) => {
          const Icon = KPI_ICONS[key] || Wallet;
          const pct = Math.min(100, Math.max(0, metric?.progress_percent || 0));
          const barColor =
            metric?.status === 'danger'
              ? 'bg-red-500'
              : metric?.status === 'warning'
              ? 'bg-[#F59E0B]'
              : metric?.status === 'success'
              ? 'bg-[#16A34A]'
              : 'bg-[#351078]';

          return (
            <div key={key} className="fg-card p-5 flex flex-col justify-between gap-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-xs font-bold text-[#5B4B7A]">{metric?.label}</p>
                  <p className="font-display font-extrabold text-2xl text-[#230852] mt-1">
                    {metric?.unit === '₹'
                      ? `₹${Number(metric?.value || 0).toLocaleString()}`
                      : `${Number(metric?.value || 0).toLocaleString()} ${metric?.unit || ''}`}
                  </p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-[#F2ECFF] border border-[#ADD8E6] text-[#351078] flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5" />
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="w-full h-1.5 rounded-full bg-[#F2ECFF] overflow-hidden">
                  <div
                    className={`h-full rounded-full ${barColor} transition-all duration-300`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <div className="flex items-center justify-between gap-2 text-[11px]">
                  <span className="text-[#5B4B7A] font-medium truncate">{metric?.comparison_note}</span>
                  {canEditBudget && (
                    <button
                      type="button"
                      onClick={() => setEditingBudget((s) => !s)}
                      className="text-[#351078] font-bold hover:underline flex-shrink-0"
                    >
                      {overview.budget_configured ? 'Adjust' : 'Set Budget'}
                    </button>
                  )}
                </div>

                {canEditBudget && editingBudget && (
                  <form onSubmit={handleBudgetSubmit} className="flex items-center gap-1.5 pt-1">
                    <input
                      type="number"
                      min="300"
                      step="100"
                      value={budgetDraft}
                      onChange={(e) => setBudgetDraft(e.target.value)}
                      placeholder="Monthly ₹"
                      className="w-full px-2.5 py-1 rounded-lg bg-[#F2ECFF] border border-[#D8C5FF] text-xs font-bold text-[#230852]"
                    />
                    <button
                      type="submit"
                      className="px-2.5 py-1 rounded-lg bg-[#351078] text-white text-xs font-bold"
                    >
                      Save
                    </button>
                  </form>
                )}
              </div>
            </div>
          );
        })}
      </section>

      {/* 3. Active Category Targets, Guidance & Suggested 5-Meal Plan */}
      <section className="fg-card p-5 sm:p-6 space-y-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#F2ECFF] pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 rounded-full bg-[#C6FF00] text-[#230852] text-[11px] font-extrabold uppercase">
                {activeCat.label || 'All Categories'}
              </span>
              <span className="text-xs font-semibold text-[#5B4B7A]">
                Daily Reference Targets &amp; Meal Allocation
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#230852]">{activeCat.description}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {[
              { label: 'Calories', val: `${activeCat.daily_calorie_target || 2000} kcal/day` },
              { label: 'Protein', val: `${activeCat.protein_goal_g || 0}g` },
              { label: 'Carbs', val: `${activeCat.carbs_goal_g || 0}g` },
              { label: 'Fat', val: `${activeCat.fat_goal_g || 0}g` },
              { label: 'Fiber', val: `${activeCat.fiber_goal_g || 30}g` },
            ].map((t) => (
              <div
                key={t.label}
                className="px-3 py-1.5 rounded-xl bg-[#EEF8FC] border border-[#ADD8E6] text-xs"
              >
                <span className="text-[#5B4B7A] font-semibold mr-1">{t.label}:</span>
                <strong className="text-[#351078]">{t.val}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Informational Medical Guidance Banner */}
        {activeCat.informational_guidance && (
          <div
            className={`p-3.5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs ${
              activeCat.recommend_professional_advice
                ? 'bg-amber-50/70 border-amber-200 text-amber-950'
                : 'bg-[#EEF8FC] border-[#ADD8E6] text-[#230852]'
            }`}
          >
            <div className="flex items-start gap-2.5">
              <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#351078]" />
              <span>{activeCat.informational_guidance}</span>
            </div>
            {activeCat.recommend_professional_advice && onNavigate && (
              <button
                type="button"
                onClick={() => onNavigate('doctors')}
                className="px-3 py-1.5 rounded-lg bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center gap-1.5 self-start sm:self-auto flex-shrink-0"
              >
                <Stethoscope className="w-3.5 h-3.5 text-[#C6FF00]" />
                <span>Consult Dietitian / Doctor</span>
              </button>
            )}
          </div>
        )}

        {/* Suggested 5-Meal Daily Schedule */}
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <h3 className="font-bold text-sm text-[#351078] flex items-center gap-2">
              <Utensils className="w-4 h-4 text-[#351078]" />
              <span>Suggested Daily Meal Plan ({activeCat.label})</span>
            </h3>
            {onApplyCategoryPlan && (
              <button
                type="button"
                onClick={onApplyCategoryPlan}
                disabled={applyingPlan}
                className="px-3 py-1.5 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center gap-1.5 disabled:opacity-50"
              >
                <Plus className="w-3.5 h-3.5 text-[#C6FF00]" />
                <span>{applyingPlan ? 'Logging...' : 'Log Today’s Plan Meals'}</span>
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {suggestedMeals.map((slot) => (
              <div
                key={slot.meal_type}
                className="p-3.5 rounded-xl bg-[#FAF7FF] border border-[#E5DAFB] flex flex-col justify-between gap-2"
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-[10px] font-extrabold uppercase tracking-wider text-[#351078]">
                      {slot.meal_label}
                    </span>
                    <span className="text-xs font-extrabold text-[#230852]">
                      ~₹{Math.round(slot.estimated_cost_inr)}
                    </span>
                  </div>
                  <p className="font-bold text-xs text-[#230852] leading-snug">{slot.food_name}</p>
                  <p className="text-[11px] text-[#5B4B7A]">{slot.quantity}</p>
                </div>
                <div className="pt-2 border-t border-[#E5DAFB] flex items-center justify-between text-[10px] font-bold text-[#5B4B7A]">
                  <span>{Math.round(slot.calories_kcal)} kcal</span>
                  <span>{slot.protein_g}g P</span>
                  <span>{slot.carbs_g}g C</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. Simplified Nutrient Analysis Section */}
      <NutritionAnalyticsSection
        overview={overview}
        onOpenLogModal={onOpenLogModal}
        onApplyCategoryPlan={onApplyCategoryPlan}
        applyingPlan={applyingPlan}
      />

      {/* 5. Budget Analysis Section */}
      <BudgetAnalyticsSection
        overview={overview}
        onOpenLogModal={onOpenLogModal}
        onOpenBudgetPlanner={() => onNavigate && onNavigate('budget')}
      />

      {/* 6. Recommended Foods Grid (with Add to My Food Cart!) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div>
            <h2 className="font-display font-extrabold text-lg sm:text-xl text-[#351078]">
              Recommended Foods — {activeCat.label}
            </h2>
            <p className="text-xs text-[#5B4B7A]">
              Verified ICMR-NIN &amp; USDA wholefoods — add any item directly to My Food Cart
            </p>
          </div>
          <div className="flex items-center gap-2">
            {onNavigate && (
              <button
                type="button"
                onClick={() => onNavigate('cart')}
                className="px-3.5 py-2 rounded-xl bg-[#351078] text-white text-xs font-bold"
              >
                Open My Food Cart
              </button>
            )}
            {onNavigate && (
              <button
                type="button"
                onClick={() => onNavigate('categories')}
                className="px-3.5 py-2 rounded-xl bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#351078] text-xs font-bold border border-[#ADD8E6]"
              >
                Browse All Foods
              </button>
            )}
          </div>
        </div>

        {recommendedFoods.length === 0 ? (
          <div className="fg-card p-8 text-center text-xs text-[#5B4B7A]">
            No foods matched your current search filter. Try clearing the search box.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {recommendedFoods.slice(0, 4).map((food) => (
              <FoodCardDetailed
                key={food.id}
                food={food}
                isInCart={cartFoodIds.has(food.id)}
                onAddToCart={onAddToCart}
                onLogFood={onLogSpecificFood}
                onAskGenie={(q, f) => onAskGenie && onAskGenie(q, f)}
              />
            ))}
          </div>
        )}
      </section>

      {/* 7. Bottom Row: Smart Food Insights + Recent Activity */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-5 space-y-4">
          <div className="fg-card p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-display font-bold text-base text-[#351078] flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-[#351078]" />
                <span>Smart Food Insights</span>
              </h2>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#C6FF00] text-[#230852]">
                Live Data
              </span>
            </div>

            <div className="space-y-2.5">
              {insights.map((ins) => (
                <div
                  key={ins.id}
                  className="p-3.5 rounded-xl bg-[#FAF7FF] border border-[#E5DAFB] flex items-start gap-3"
                >
                  {ins.severity === 'warning' ? (
                    <AlertTriangle className="w-4 h-4 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                  ) : ins.severity === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 text-[#16A34A] flex-shrink-0 mt-0.5" />
                  ) : (
                    <Info className="w-4 h-4 text-[#351078] flex-shrink-0 mt-0.5" />
                  )}
                  <div className="space-y-0.5">
                    <p className="text-xs font-bold text-[#230852]">{ins.title}</p>
                    <p className="text-xs text-[#5B4B7A] leading-relaxed">{ins.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="fg-card p-5 space-y-3 bg-[#EEF8FC] border-[#ADD8E6]">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-[#351078] flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#351078]" />
                <span>Quick Ask Genie AI</span>
              </h3>
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('recommendations')}
                className="text-xs font-bold text-[#351078] hover:underline"
              >
                Open Full Chat
              </button>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (quickGenieQuery.trim() && onAskGenie) {
                  onAskGenie(quickGenieQuery.trim());
                  setQuickGenieQuery('');
                }
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={quickGenieQuery}
                onChange={(e) => setQuickGenieQuery(e.target.value)}
                placeholder={`Ask Genie about ${activeCat.label || 'nutrition'} or your cart...`}
                className="flex-1 px-3.5 py-2 rounded-xl bg-white border border-[#ADD8E6] text-xs text-[#230852] focus:outline-none focus:border-[#351078]"
              />
              <button
                type="submit"
                disabled={!quickGenieQuery.trim()}
                className="px-3.5 py-2 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center gap-1 disabled:opacity-50"
              >
                <MessageSquare className="w-3.5 h-3.5 text-[#C6FF00]" />
                <span>Ask</span>
              </button>
            </form>
          </div>
        </div>

        <div className="lg:col-span-7 fg-card p-5 space-y-4">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div>
              <h2 className="font-display font-bold text-base text-[#351078] flex items-center gap-2">
                <Clock className="w-5 h-5 text-[#351078]" />
                <span>Recent Activity &amp; Logged Entries</span>
              </h2>
              <p className="text-xs text-[#5B4B7A]">
                Added meals, purchases, food cart updates, and recommendations
              </p>
            </div>
            {onOpenLogModal && (
              <button
                type="button"
                onClick={onOpenLogModal}
                className="px-3 py-1.5 rounded-xl bg-[#EEF8FC] text-[#351078] text-xs font-bold border border-[#ADD8E6]"
              >
                + Log Entry
              </button>
            )}
          </div>

          {foodLogs.length > 0 && (
            <div className="overflow-x-auto rounded-xl border border-[#E5DAFB]">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="bg-[#F2ECFF] text-[#351078] font-bold uppercase text-[10px]">
                    <th className="py-2.5 px-3">Food / Item</th>
                    <th className="py-2.5 px-3">Slot</th>
                    <th className="py-2.5 px-3">Calories</th>
                    <th className="py-2.5 px-3">Protein</th>
                    <th className="py-2.5 px-3">Cost</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F2ECFF]">
                  {foodLogs.slice(0, 6).map((log) => (
                    <tr key={log.id} className="hover:bg-[#FAF7FF]">
                      <td className="py-2 px-3 font-bold text-[#230852]">
                        {log.food_name}
                        <span className="block text-[10px] font-normal text-[#5B4B7A]">{log.food_category}</span>
                      </td>
                      <td className="py-2 px-3 text-[#5B4B7A]">{log.meal_type}</td>
                      <td className="py-2 px-3 font-semibold text-[#230852]">{Math.round(log.calories_kcal)} kcal</td>
                      <td className="py-2 px-3 text-[#5B4B7A]">{log.protein_g}g</td>
                      <td className="py-2 px-3 font-bold text-[#351078]">₹{Number(log.cost_inr || 0).toFixed(0)}</td>
                      <td className="py-2 px-3 text-right">
                        {onDeleteLog && (
                          <button
                            type="button"
                            onClick={() => onDeleteLog(log.id)}
                            className="p-1.5 rounded-lg text-[#5B4B7A] hover:text-red-600 hover:bg-red-50"
                            title="Delete logged entry"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {recentActivity.length === 0 ? (
            <div className="p-8 rounded-xl bg-[#FAF7FF] border border-[#E5DAFB] text-center space-y-2">
              <p className="text-xs font-bold text-[#230852]">No recent activity recorded yet</p>
              <p className="text-xs text-[#5B4B7A]">
                Log a meal, add items to My Food Cart, or ask Genie for a recommendation to populate your timeline.
              </p>
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {recentActivity.map((act) => (
                <div
                  key={act.id}
                  className="p-3 rounded-xl bg-[#FAF7FF] border border-[#E5DAFB] flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-[#230852] truncate">{act.title}</p>
                    <p className="text-[11px] text-[#5B4B7A] truncate">
                      {act.subtitle || act.activity_type.replace('_', ' ')} •{' '}
                      {new Date(act.timestamp).toLocaleString([], {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {act.amount_inr !== null && act.amount_inr !== undefined && (
                      <span className="px-2 py-0.5 rounded-lg bg-[#EEF8FC] border border-[#ADD8E6] text-[#351078] text-[11px] font-bold">
                        ₹{Math.round(act.amount_inr).toLocaleString()}
                      </span>
                    )}
                    <span className="px-2 py-0.5 rounded-full bg-green-50 text-[#16A34A] border border-green-200 text-[10px] font-bold uppercase">
                      {act.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default DashboardView;
