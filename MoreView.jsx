import React from 'react';
import {
  TrendingUp, TrendingDown, Scale, Wallet, MapPin, Bookmark, Settings,
  ArrowRight, ShieldCheck, Sparkles, ChevronRight
} from 'lucide-react';

export const MoreView = ({ onNavigate, onOpenAuth }) => {
  const tools = [
    {
      id: 'goal-gain',
      title: 'Weight Gain Planner',
      badge: 'Goal Planner',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-200',
      desc: 'Calorie & protein-dense meal plans designed for healthy, steady mass accumulation with bioavailable Indian wholefoods.',
      icon: TrendingUp,
      action: 'Open Weight Gain Plan',
    },
    {
      id: 'goal-loss',
      title: 'Weight Loss Planner',
      badge: 'Goal Planner',
      badgeColor: 'bg-rose-100 text-rose-800 border-rose-200',
      desc: 'High-satiety, high-fiber, and low glycemic load meal structures to promote fat loss without nutritional deficiencies.',
      icon: TrendingDown,
      action: 'Open Weight Loss Plan',
    },
    {
      id: 'goal-maintain',
      title: 'Weight Maintenance Planner',
      badge: 'Goal Planner',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      desc: 'Balanced daily energy equilibrium and seasonal wholefoods to maintain metabolic health and steady vitality.',
      icon: Scale,
      action: 'Open Maintenance Plan',
    },
    {
      id: 'budget',
      title: 'Budget Planner',
      badge: '₹ Calculator',
      badgeColor: 'bg-lime-electric/30 text-royal-deep border-lime-dark/30',
      desc: 'Set daily, weekly, or monthly food budgets in ₹ and generate complete 7-day meal plans with verified local mandi prices.',
      icon: Wallet,
      action: 'Open Budget Planner',
    },
    {
      id: 'doctors',
      title: 'Nearby Doctors',
      badge: 'Clinical Directory',
      badgeColor: 'bg-sky-100 text-sky-800 border-sky-200',
      desc: 'Find certified clinical dietitians, dermatologists, and physicians near your location with verified contact details.',
      icon: MapPin,
      action: 'Find Doctors',
    },
    {
      id: 'saved',
      title: 'My Saved Plans',
      badge: 'Saved Items',
      badgeColor: 'bg-lavender-mist text-royal border-lavender-border',
      desc: 'Access your bookmarked wholefoods, saved 7-day budget meal plans, and previous conversation records.',
      icon: Bookmark,
      action: 'View Saved Plans',
    },
    {
      id: 'profile',
      title: 'Profile and Settings',
      badge: 'Preferences',
      badgeColor: 'bg-purple-100 text-purple-800 border-purple-200',
      desc: 'Manage your health profile, dietary preferences, food allergies, and account credentials securely.',
      icon: Settings,
      action: 'Open Profile & Settings',
    },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-lavender-mist border border-lavender-border text-royal text-xs font-bold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5 text-royal" />
          <span>Additional Features &amp; Planners</span>
        </div>
        <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-royal tracking-tight">
          More FoodGenie Tools
        </h1>
        <p className="text-xs sm:text-sm text-royal/70 max-w-2xl leading-relaxed">
          Select any of the 7 specialized nutrition, budget, and clinical discovery features below to customize your health journey.
        </p>
      </div>

      {/* Grid of the 7 Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {tools.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.id}
              className="fg-card p-5 flex flex-col justify-between space-y-4 hover:border-royal/40 transition-all hover:shadow-card group"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="w-10 h-10 rounded-xl bg-royal text-lime-electric flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                </div>

                <div>
                  <h2 className="font-display font-bold text-base text-royal group-hover:text-royal-light transition-colors">
                    {item.title}
                  </h2>
                  <p className="text-xs text-royal/70 mt-1 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => onNavigate && onNavigate(item.id)}
                className="w-full py-2.5 px-3 rounded-xl bg-lavender-mist hover:bg-royal hover:text-white text-royal text-xs font-bold flex items-center justify-center gap-1.5 border border-lavender-border transition-all"
              >
                <span>{item.action}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>

      {/* Trust & Safety Banner */}
      <div className="fg-card p-4 sm:p-5 flex items-center gap-3.5 bg-lavender-light border border-lavender-border text-xs text-royal/80">
        <ShieldCheck className="w-5 h-5 text-lime-dark flex-shrink-0" />
        <p className="leading-relaxed">
          All meal plans, price calculations, and doctor directories are calibrated to certified ICMR-NIN, APMC/Rythu Bazar, and verified medical registry standards.
        </p>
      </div>
    </div>
  );
};

export default MoreView;
