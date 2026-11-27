import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts';
import { Activity, Plus, CheckCircle2, Info, Sparkles, ShieldCheck } from 'lucide-react';

// Theme palette: Royal Purple, Light Blue, Electric Lime
const MACRO_COLORS = ['#351078', '#ADD8E6', '#16A34A'];

export const NutritionAnalyticsSection = ({
  overview,
  onOpenLogModal,
  onApplyCategoryPlan,
  applyingPlan = false,
}) => {
  if (!overview) return null;

  const {
    has_nutrition_logs = false,
    daily_calorie_target = 2000,
    logged_daily_average = {},
    macro_distribution = [],
    nutrient_progress = [],
    vitamins_summary = [],
    minerals_summary = [],
    active_category_info = {},
  } = overview;

  // Keep only core essential macro indicators + daily targets
  const coreMacros = [
    {
      label: 'Total Calories',
      actual: has_nutrition_logs ? Math.round(logged_daily_average.calories_kcal || 0) : 0,
      goal: daily_calorie_target,
      unit: 'kcal',
      accentBg: 'bg-[#F2ECFF]',
      accentBorder: 'border-[#D8C5FF]',
    },
    {
      label: 'Protein',
      actual: has_nutrition_logs ? Number(logged_daily_average.protein_g || 0) : 0,
      goal: active_category_info.protein_goal_g || 60,
      unit: 'g',
      accentBg: 'bg-[#EEF8FC]',
      accentBorder: 'border-[#ADD8E6]',
    },
    {
      label: 'Carbohydrates',
      actual: has_nutrition_logs ? Number(logged_daily_average.carbs_g || 0) : 0,
      goal: active_category_info.carbs_goal_g || 250,
      unit: 'g',
      accentBg: 'bg-[#F2ECFF]',
      accentBorder: 'border-[#D8C5FF]',
    },
    {
      label: 'Fats',
      actual: has_nutrition_logs ? Number(logged_daily_average.fat_g || 0) : 0,
      goal: active_category_info.fat_goal_g || 60,
      unit: 'g',
      accentBg: 'bg-[#EEF8FC]',
      accentBorder: 'border-[#ADD8E6]',
    },
  ];

  // Filter out optional sugar from primary progress bar list unless logged
  const visibleProgress = nutrient_progress.filter(
    (np) => np.name !== 'Sugar' || np.data_available
  );

  return (
    <section className="space-y-5">
      {/* Clean Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="font-display font-extrabold text-lg sm:text-xl text-[#351078] flex items-center gap-2">
            <Activity className="w-5 h-5 text-[#351078]" />
            <span>Nutrient Analysis</span>
          </h2>
          <p className="text-xs text-[#5B4B7A]">
            Daily nutrition summary &amp; target progress grounded in ICMR-NIN and USDA reference values
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {onApplyCategoryPlan && (
            <button
              type="button"
              onClick={onApplyCategoryPlan}
              disabled={applyingPlan}
              className="px-3.5 py-2 rounded-xl bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#230852] text-xs font-bold border border-[#ADD8E6] flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-[#351078]" />
              <span>{applyingPlan ? 'Logging Plan...' : `Log ${active_category_info?.label || 'Category'} Meals`}</span>
            </button>
          )}
          {onOpenLogModal && (
            <button
              type="button"
              onClick={onOpenLogModal}
              className="px-4 py-2 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center gap-1.5 shadow-xs transition-colors"
            >
              <Plus className="w-3.5 h-3.5 text-[#C6FF00]" />
              <span>Log Food</span>
            </button>
          )}
        </div>
      </div>

      {/* 4 Essential Macro Summary Cards (Calories, Protein, Carbs, Fats + Daily Target Progress) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {coreMacros.map((m) => {
          const pct = m.goal > 0 ? Math.min(100, Math.round((m.actual / m.goal) * 100)) : 0;
          return (
            <div key={m.label} className="fg-card p-4 space-y-2.5">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-bold text-[#5B4B7A]">{m.label}</span>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${m.accentBg} border ${m.accentBorder} text-[#351078]`}>
                  {pct}% of goal
                </span>
              </div>

              <div className="flex items-baseline justify-between gap-2">
                <p className="font-display font-extrabold text-2xl text-[#230852]">
                  {m.actual} <span className="text-xs font-semibold text-[#5B4B7A]">{m.unit}</span>
                </p>
                <span className="text-[11px] font-semibold text-[#5B4B7A]">
                  Target: <strong className="text-[#351078]">{m.goal} {m.unit}</strong>
                </span>
              </div>

              <div className="w-full h-2 rounded-full bg-[#F2ECFF] overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${
                    pct >= 90 ? 'bg-[#16A34A]' : pct >= 50 ? 'bg-[#351078]' : 'bg-[#ADD8E6]'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Essential Progress & Macro Split Row (No cluttered or duplicate charts) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Progress Towards Daily Nutritional Target */}
        <div className="lg:col-span-7 fg-card p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-[#F2ECFF] pb-3">
            <div>
              <h3 className="font-bold text-sm text-[#351078]">
                Daily Nutritional Target &amp; Progress
              </h3>
              <p className="text-xs text-[#5B4B7A]">
                Daily intake progress vs {active_category_info?.label || 'active'} targets
              </p>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-[#C6FF00] text-[#230852] text-[10px] font-extrabold">
              {has_nutrition_logs ? 'Active Tracking' : 'Awaiting Logs'}
            </span>
          </div>

          <div className="space-y-3.5">
            {visibleProgress.map((np) => {
              const pct = Math.min(100, np.percent_achieved || 0);
              return (
                <div key={np.name} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-[#230852]">{np.name}</span>
                    <span className="text-[#5B4B7A]">
                      <strong className="text-[#351078]">{np.actual ?? 0}</strong> / {np.goal} {np.unit}{' '}
                      <span className="font-bold text-[#351078]">({Math.round(np.percent_achieved || 0)}%)</span>
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#F2ECFF] overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        pct >= 85 ? 'bg-[#16A34A]' : pct >= 45 ? 'bg-[#351078]' : 'bg-[#ADD8E6]'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Single Purposeful Donut Chart: Macronutrient Balance */}
        <div className="lg:col-span-5 fg-card p-5 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-[#351078]">Macronutrient Energy Split</h3>
            <p className="text-xs text-[#5B4B7A]">Protein vs Carbohydrates vs Fats</p>
          </div>

          {!has_nutrition_logs || macro_distribution.length === 0 ? (
            <div className="py-8 text-center space-y-2 bg-[#EEF8FC] rounded-xl border border-[#ADD8E6] my-3 px-4">
              <Info className="w-6 h-6 text-[#351078] mx-auto" />
              <p className="text-xs font-bold text-[#230852]">No meals logged yet for this period</p>
              <p className="text-[11px] text-[#5B4B7A]">
                Log a meal or apply today&apos;s suggested plan to inspect your macro breakdown.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 items-center gap-3 my-2">
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={macro_distribution}
                      dataKey="percentage"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={66}
                      paddingAngle={3}
                    >
                      {macro_distribution.map((_, idx) => (
                        <Cell key={idx} fill={MACRO_COLORS[idx % MACRO_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(val, name, props) => [`${props?.payload?.grams}g (${val}%)`, name]}
                      contentStyle={{ borderRadius: '12px', border: '1px solid #ADD8E6', fontSize: '12px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 text-xs">
                {macro_distribution.map((m, i) => (
                  <div key={m.name} className="p-2 rounded-xl bg-[#F2ECFF]/60 flex items-center justify-between">
                    <span className="flex items-center gap-2 text-[#230852] font-semibold">
                      <span
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: MACRO_COLORS[i % MACRO_COLORS.length] }}
                      />
                      <span>{m.name}</span>
                    </span>
                    <span className="font-extrabold text-[#351078]">
                      {m.grams}g ({m.percentage}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Compact Important Vitamins & Important Minerals Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Important Vitamins */}
        <div className="fg-card p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-[#F2ECFF] pb-2.5">
            <h3 className="font-bold text-sm text-[#351078] flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#351078]" />
              <span>Important Vitamins (vs Daily RDA)</span>
            </h3>
            <span className="text-[11px] font-semibold text-[#5B4B7A] bg-[#EEF8FC] px-2.5 py-0.5 rounded-full border border-[#ADD8E6]">
              {vitamins_summary.length} Tracked
            </span>
          </div>
          <div className="space-y-2.5">
            {vitamins_summary.map((v) => {
              const pct = Math.min(100, Math.round(v.percent_achieved || 0));
              return (
                <div key={v.name} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-[#230852]">{v.name}</span>
                    <span className="text-[#5B4B7A]">
                      <strong className="text-[#351078]">{v.actual ?? 0}</strong> / {v.goal} {v.unit} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[#F2ECFF] overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[#351078] transition-all duration-300"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Important Minerals */}
        <div className="fg-card p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-[#F2ECFF] pb-2.5">
            <h3 className="font-bold text-sm text-[#351078] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#351078]" />
              <span>Important Minerals (vs Daily RDA)</span>
            </h3>
            <span className="text-[11px] font-semibold text-[#5B4B7A] bg-[#EEF8FC] px-2.5 py-0.5 rounded-full border border-[#ADD8E6]">
              {minerals_summary.length} Tracked
            </span>
          </div>
          <div className="space-y-2.5">
            {minerals_summary.map((m) => {
              const pct = Math.min(100, Math.round(m.percent_achieved || 0));
              return (
                <div key={m.name} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-[#230852]">{m.name}</span>
                    <span className="text-[#5B4B7A]">
                      <strong className="text-[#351078]">{m.actual ?? 0}</strong> / {m.goal} {m.unit} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[#F2ECFF] overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[#ADD8E6] transition-all duration-300"
                      style={{ width: `${pct}%`, backgroundColor: pct >= 70 ? '#351078' : '#7EC8E3' }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};

export default NutritionAnalyticsSection;
