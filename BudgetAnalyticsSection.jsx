import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Wallet, TrendingUp, PieChart as PieIcon, Plus, AlertTriangle } from 'lucide-react';

// Theme palette: Royal Purple, Light Blue, Electric Lime highlights, semantic status colors
const CHART_COLORS = ['#351078', '#ADD8E6', '#6D28D9', '#16A34A', '#F59E0B', '#60A5FA', '#5B4B7A'];

export const CircularBudgetGauge = ({ percent = 0, spent = 0, budget = 0, budgetConfigured = false }) => {
  const clamped = Math.min(100, Math.max(0, Number(percent) || 0));
  const radius = 56;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clamped / 100) * circumference;

  const strokeColor =
    !budgetConfigured
      ? '#ADD8E6'
      : percent > 100
      ? '#DC2626'
      : percent >= 85
      ? '#F59E0B'
      : '#351078';

  return (
    <div className="flex flex-col items-center justify-center py-2">
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-36 h-36 -rotate-90" viewBox="0 0 140 140">
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke="#F2ECFF"
            strokeWidth="12"
          />
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 450ms ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-display font-extrabold text-2xl text-[#230852]">
            {budgetConfigured ? `${percent.toFixed(0)}%` : '—'}
          </span>
          <span className="text-[11px] font-semibold text-[#5B4B7A]">Utilized</span>
        </div>
      </div>

      <div className="mt-3 text-center space-y-0.5">
        <p className="text-xs font-bold text-[#230852]">
          ₹{Number(spent || 0).toLocaleString()} spent of ₹{Number(budget || 0).toLocaleString()}
        </p>
        <p className="text-[11px] text-[#5B4B7A]">
          {!budgetConfigured
            ? 'Configure your budget to activate utilization tracking'
            : percent > 100
            ? 'Spending exceeded target budget'
            : percent >= 85
            ? 'Approaching budget threshold'
            : 'Healthy spending pace'}
        </p>
      </div>
    </div>
  );
};

export const BudgetAnalyticsSection = ({
  overview,
  onOpenLogModal,
  onOpenBudgetPlanner,
}) => {
  const [pieMode, setPieMode] = useState('actual');

  if (!overview) return null;

  const {
    daily_budget_inr = 0,
    weekly_budget_inr = 0,
    monthly_budget_inr = 0,
    total_food_expenses_inr = 0,
    remaining_balance_inr = 0,
    avg_daily_spending_inr = 0,
    budget_utilization_percent = 0,
    budget_configured = false,
    has_expense_logs = false,
    budget_vs_spending = [],
    daily_expenses_series = [],
    category_spending = [],
    planned_category_allocation = [],
    date_range = 'weekly',
  } = overview;

  const periodBudget =
    date_range === 'daily'
      ? daily_budget_inr
      : date_range === 'monthly'
      ? monthly_budget_inr
      : weekly_budget_inr;

  const activePieData =
    pieMode === 'actual' && has_expense_logs && category_spending.length > 0
      ? category_spending
      : planned_category_allocation;

  const showingPlannedFallback = pieMode === 'actual' && (!has_expense_logs || category_spending.length === 0);

  return (
    <section className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="font-display font-extrabold text-lg sm:text-xl text-[#351078] flex items-center gap-2">
            <Wallet className="w-5 h-5 text-[#351078]" />
            <span>Budget Analysis</span>
          </h2>
          <p className="text-xs text-[#5B4B7A]">
            Real-time expense tracking, daily spend averages, and category allocation in INR
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onOpenLogModal && (
            <button
              type="button"
              onClick={onOpenLogModal}
              className="px-3 py-1.5 rounded-xl bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#230852] text-xs font-bold border border-[#ADD8E6] flex items-center gap-1 transition-colors"
            >
              <Plus className="w-3.5 h-3.5 text-[#351078]" />
              <span>Add Expense</span>
            </button>
          )}
          {onOpenBudgetPlanner && (
            <button
              type="button"
              onClick={onOpenBudgetPlanner}
              className="px-3 py-1.5 rounded-xl bg-white hover:bg-[#F2ECFF] text-[#351078] text-xs font-bold border border-[#D8C5FF] transition-colors"
            >
              Open Full Planner
            </button>
          )}
        </div>
      </div>

      {/* Budget Summary Strip */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
        {[
          { label: 'Daily Budget', value: `₹${daily_budget_inr.toLocaleString()}`, sub: 'Per day target' },
          { label: 'Weekly Budget', value: `₹${weekly_budget_inr.toLocaleString()}`, sub: '7-day allocation' },
          { label: 'Monthly Budget', value: `₹${monthly_budget_inr.toLocaleString()}`, sub: '30-day cap' },
          { label: 'Total Food Expenses', value: `₹${total_food_expenses_inr.toLocaleString()}`, sub: `${date_range} logged` },
          {
            label: 'Remaining Balance',
            value: `₹${remaining_balance_inr.toLocaleString()}`,
            sub: remaining_balance_inr < 0 ? 'Over budget' : `${date_range} left`,
            highlight: remaining_balance_inr < 0 ? 'text-red-600' : 'text-[#16A34A]',
          },
          { label: 'Avg Daily Spending', value: `₹${avg_daily_spending_inr.toLocaleString()}`, sub: 'Active spend days' },
        ].map((item) => (
          <div key={item.label} className="fg-card p-3.5 space-y-1">
            <p className="text-[11px] font-bold text-[#5B4B7A] truncate">{item.label}</p>
            <p className={`font-display font-extrabold text-base sm:text-lg ${item.highlight || 'text-[#230852]'}`}>
              {item.value}
            </p>
            <p className="text-[10px] text-[#5B4B7A]">{item.sub}</p>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Bar Chart: Budget vs Actual Spending */}
        <div className="lg:col-span-7 fg-card p-5 space-y-3">
          <div>
            <h3 className="font-bold text-sm text-[#351078]">
              Budget vs Actual Spending ({date_range.charAt(0).toUpperCase() + date_range.slice(1)})
            </h3>
            <p className="text-xs text-[#5B4B7A]">Target allocation vs logged ₹ expenditure</p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={budget_vs_spending} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5DAFB" vertical={false} />
                <XAxis dataKey="label" tick={{ fill: '#5B4B7A', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#5B4B7A', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                <Tooltip
                  formatter={(value, name) => [`₹${Number(value).toLocaleString()}`, name]}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #ADD8E6', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="planned_budget" name="Target Budget" fill="#ADD8E6" radius={[6, 6, 0, 0]} />
                <Bar dataKey="actual_spent" name="Actual Spent" fill="#351078" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Circular Progress Gauge */}
        <div className="lg:col-span-5 fg-card p-5 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-[#351078]">Budget Utilization</h3>
            <p className="text-xs text-[#5B4B7A]">Share of active {date_range} budget spent</p>
          </div>

          <CircularBudgetGauge
            percent={budget_utilization_percent}
            spent={total_food_expenses_inr}
            budget={periodBudget}
            budgetConfigured={budget_configured}
          />

          {!budget_configured && (
            <div className="p-2.5 rounded-xl bg-[#EEF8FC] border border-[#ADD8E6] text-[11px] text-[#230852] flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-[#351078] flex-shrink-0" />
              <span>Configure your monthly budget in Profile/Settings to track utilization.</span>
            </div>
          )}
        </div>

        {/* Line Chart: Daily Expenses */}
        <div className="lg:col-span-7 fg-card p-5 space-y-3">
          <div className="flex items-center justify-between gap-2">
            <div>
              <h3 className="font-bold text-sm text-[#351078] flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-[#351078]" />
                <span>Daily Expenses Trend</span>
              </h3>
              <p className="text-xs text-[#5B4B7A]">Logged daily food spending across {overview.period_label}</p>
            </div>
            {!has_expense_logs && (
              <span className="px-2.5 py-1 rounded-full bg-[#EEF8FC] border border-[#ADD8E6] text-[#230852] text-[11px] font-semibold">
                No expenses logged yet
              </span>
            )}
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={daily_expenses_series} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5DAFB" vertical={false} />
                <XAxis dataKey="date_label" tick={{ fill: '#5B4B7A', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#5B4B7A', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                <Tooltip
                  formatter={(value) => [`₹${Number(value).toLocaleString()}`, 'Daily Expense']}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #ADD8E6', fontSize: '12px' }}
                />
                <Line
                  type="monotone"
                  dataKey="amount_inr"
                  name="Expense (₹)"
                  stroke="#351078"
                  strokeWidth={2.5}
                  dot={{ r: 3.5, fill: '#351078' }}
                  activeDot={{ r: 6, fill: '#C6FF00', stroke: '#351078', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Donut Chart: Category-wise Food Spending */}
        <div className="lg:col-span-5 fg-card p-5 space-y-3">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div>
              <h3 className="font-bold text-sm text-[#351078] flex items-center gap-1.5">
                <PieIcon className="w-4 h-4 text-[#351078]" />
                <span>Category-wise Food Spending</span>
              </h3>
              <p className="text-xs text-[#5B4B7A]">
                {showingPlannedFallback
                  ? 'Showing planned category allocation (no expenses logged yet)'
                  : pieMode === 'actual'
                  ? 'Based on logged food expenses'
                  : 'Recommended budget split by category'}
              </p>
            </div>
            <div className="inline-flex bg-[#F2ECFF] p-0.5 rounded-lg border border-[#D8C5FF] text-[11px] font-bold">
              <button
                type="button"
                onClick={() => setPieMode('actual')}
                className={`px-2 py-1 rounded-md ${pieMode === 'actual' ? 'bg-[#351078] text-white' : 'text-[#5B4B7A]'}`}
              >
                Actual
              </button>
              <button
                type="button"
                onClick={() => setPieMode('planned')}
                className={`px-2 py-1 rounded-md ${pieMode === 'planned' ? 'bg-[#351078] text-white' : 'text-[#5B4B7A]'}`}
              >
                Target Split
              </button>
            </div>
          </div>

          {activePieData.length === 0 ? (
            <div className="h-56 flex items-center justify-center text-xs text-[#5B4B7A] text-center px-4">
              Set a budget or log purchases to inspect spending distribution across food groups.
            </div>
          ) : (
            <div className="h-56 w-full flex flex-col sm:flex-row items-center">
              <div className="w-full sm:w-1/2 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={activePieData}
                      dataKey="percentage"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      innerRadius={42}
                      outerRadius={70}
                      paddingAngle={2}
                    >
                      {activePieData.map((_, i) => (
                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(val, name, props) => [
                        `₹${Number(props?.payload?.amount_inr || 0).toLocaleString()} (${val}%)`,
                        name,
                      ]}
                      contentStyle={{ borderRadius: '12px', border: '1px solid #ADD8E6', fontSize: '12px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-full sm:w-1/2 space-y-1.5 text-xs overflow-y-auto max-h-48 pl-1">
                {activePieData.map((item, i) => (
                  <div key={item.category} className="flex items-center justify-between gap-2">
                    <span className="flex items-center gap-1.5 text-[#230852] truncate">
                      <span
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
                      />
                      <span className="truncate">{item.category}</span>
                    </span>
                    <span className="font-bold text-[#351078] flex-shrink-0">{item.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default BudgetAnalyticsSection;
