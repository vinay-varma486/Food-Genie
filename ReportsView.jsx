import React from 'react';
import { FileBarChart2, Download, CheckCircle2, AlertTriangle, Trash2 } from 'lucide-react';

export const ReportsView = ({ overview, onDeleteLog, onOpenLogModal }) => {
  if (!overview) return null;

  const foodLogs = overview.food_logs || [];
  const nutrientProgress = overview.nutrient_progress || [];
  const vitamins = overview.vitamins_summary || [];
  const minerals = overview.minerals_summary || [];

  const handleExportCsv = () => {
    const rows = [
      ['Date', 'Food Name', 'Category', 'Meal Type', 'Entry Type', 'Quantity (g)', 'Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)', 'Cost (INR)'],
      ...foodLogs.map((l) => [
        new Date(l.logged_at).toISOString(),
        `"${String(l.food_name || '').replace(/"/g, '""')}"`,
        `"${String(l.food_category || '')}"`,
        `"${String(l.meal_type || '')}"`,
        l.entry_type,
        l.quantity_g,
        l.calories_kcal,
        l.protein_g,
        l.carbs_g,
        l.fat_g,
        l.fiber_g,
        l.cost_inr,
      ]),
    ];
    const csv = rows.map((r) => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `foodgenie-report-${overview.date_range}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportJson = () => {
    const report = {
      generated_at: new Date().toISOString(),
      period: overview.date_range,
      category: overview.active_category_info?.label,
      budget_summary: {
        monthly_budget_inr: overview.monthly_budget_inr,
        period_budget_inr: overview.total_budget_card?.value,
        spent_inr: overview.total_food_expenses_inr,
        remaining_inr: overview.remaining_balance_inr,
        utilization_percent: overview.budget_utilization_percent,
      },
      nutrition_daily_average: overview.logged_daily_average,
      logs_count: foodLogs.length,
      logs: foodLogs,
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `foodgenie-report-${overview.date_range}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display font-extrabold text-2xl text-[#230852] flex items-center gap-2.5">
            <FileBarChart2 className="w-6 h-6 text-[#351078]" />
            <span>Nutrition &amp; Budget Reports</span>
          </h1>
          <p className="text-xs sm:text-sm text-[#5B4B7A] mt-0.5">
            Period: <strong className="text-[#230852] capitalize">{overview.date_range}</strong> •{' '}
            Category: <strong className="text-[#351078]">{overview.active_category_info?.label}</strong>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleExportCsv}
            disabled={foodLogs.length === 0}
            className="px-3.5 py-2 rounded-xl bg-white hover:bg-[#EEF8FC] text-[#351078] text-xs font-bold border border-[#ADD8E6] flex items-center gap-1.5 disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
          <button
            type="button"
            onClick={handleExportJson}
            className="px-3.5 py-2 rounded-xl bg-[#351078] hover:bg-[#351078] text-white text-xs font-bold flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download JSON</span>
          </button>
        </div>
      </div>

      {/* Period Audit Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Active Budget', val: `₹${Number(overview.total_budget_card?.value || 0).toLocaleString()}`, note: overview.date_range },
          { label: 'Total Spent', val: `₹${Number(overview.total_food_expenses_inr || 0).toLocaleString()}`, note: `${overview.budget_utilization_percent}% utilized` },
          { label: 'Total Calories Logged', val: `${Math.round(overview.total_calories_card?.value || 0).toLocaleString()} kcal`, note: `${foodLogs.length} entries` },
          { label: 'Saved Plans / Foods', val: `${overview.saved_plans_count} / ${overview.saved_foods_count}`, note: 'In account' },
        ].map((card) => (
          <div key={card.label} className="fg-card p-4 space-y-1">
            <p className="text-xs font-bold text-[#5B4B7A]">{card.label}</p>
            <p className="font-display font-extrabold text-xl text-[#230852]">{card.val}</p>
            <p className="text-[11px] text-[#351078] font-semibold capitalize">{card.note}</p>
          </div>
        ))}
      </div>

      {/* Nutrient Attainment Table */}
      <div className="fg-card p-5 space-y-3">
        <h2 className="font-bold text-base text-[#230852]">Macro &amp; Micronutrient Goal Report</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="bg-[#FAF7FF] text-[#5B4B7A] uppercase text-[10px] font-bold">
                <th className="py-2.5 px-3">Nutrient</th>
                <th className="py-2.5 px-3">Daily Average</th>
                <th className="py-2.5 px-3">Target / RDA</th>
                <th className="py-2.5 px-3">Attainment</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {[...nutrientProgress, ...vitamins.slice(0, 4), ...minerals.slice(0, 4)].map((n) => {
                const pct = n.percent_achieved ?? 0;
                return (
                  <tr key={n.name} className="hover:bg-[#EEF8FC]/30">
                    <td className="py-2 px-3 font-bold text-[#230852]">{n.name}</td>
                    <td className="py-2 px-3">
                      {n.data_available ? `${n.actual ?? 0} ${n.unit}` : 'Unavailable in ref'}
                    </td>
                    <td className="py-2 px-3 text-[#5B4B7A]">
                      {n.goal ? `${n.goal} ${n.unit}` : '—'}
                    </td>
                    <td className="py-2 px-3 font-bold text-[#351078]">
                      {n.data_available && n.percent_achieved !== null ? `${pct}%` : '—'}
                    </td>
                    <td className="py-2 px-3">
                      {!n.data_available ? (
                        <span className="text-[11px] text-[#5B4B7A]">No logs</span>
                      ) : pct >= 80 ? (
                        <span className="inline-flex items-center gap-1 text-[#16A34A] font-bold">
                          <CheckCircle2 className="w-3.5 h-3.5" /> On Track
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[#F59E0B] font-bold">
                          <AlertTriangle className="w-3.5 h-3.5" /> Below Target
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Logged Ledger */}
      <div className="fg-card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-base text-[#230852]">Detailed Food &amp; Expense Ledger</h2>
          {onOpenLogModal && (
            <button
              type="button"
              onClick={onOpenLogModal}
              className="px-3 py-1.5 rounded-xl bg-[#EEF8FC] text-[#351078] text-xs font-bold border border-[#ADD8E6]"
            >
              + Add Log Entry
            </button>
          )}
        </div>

        {foodLogs.length === 0 ? (
          <p className="text-xs text-[#5B4B7A] py-8 text-center">
            No logged meals or expenses for this period yet. Log meals to generate exportable ledger rows.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="bg-[#FAF7FF] text-[#5B4B7A] uppercase text-[10px] font-bold">
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Food / Item</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Calories</th>
                  <th className="py-2.5 px-3">Macros (P/C/F)</th>
                  <th className="py-2.5 px-3">Cost (₹)</th>
                  <th className="py-2.5 px-3 text-right">Remove</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {foodLogs.map((l) => (
                  <tr key={l.id} className="hover:bg-[#EEF8FC]/30">
                    <td className="py-2 px-3 text-[#5B4B7A] whitespace-nowrap">
                      {new Date(l.logged_at).toLocaleDateString()}
                    </td>
                    <td className="py-2 px-3 font-bold text-[#230852]">{l.food_name}</td>
                    <td className="py-2 px-3 text-[#5B4B7A] capitalize">{l.meal_type}</td>
                    <td className="py-2 px-3 font-semibold">{Math.round(l.calories_kcal)} kcal</td>
                    <td className="py-2 px-3 text-[#5B4B7A]">
                      {l.protein_g}g / {l.carbs_g}g / {l.fat_g}g
                    </td>
                    <td className="py-2 px-3 font-bold text-[#351078]">₹{Number(l.cost_inr || 0).toFixed(0)}</td>
                    <td className="py-2 px-3 text-right">
                      {onDeleteLog && (
                        <button
                          type="button"
                          onClick={() => onDeleteLog(l.id)}
                          className="p-1.5 rounded-lg text-[#5B4B7A] hover:text-red-600"
                          title="Delete entry"
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
      </div>
    </div>
  );
};

export default ReportsView;

