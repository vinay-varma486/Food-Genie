import React from 'react';
import { ShieldCheck, Database, Wallet, MessageSquare, ArrowRight } from 'lucide-react';

export default function About({ onNavigate }) {
  const pillars = [
    {
      icon: MessageSquare,
      title: 'Conversational AI (Genie)',
      desc: 'Powered by OpenRouter AI & Genie with automatic language detection across English, Telugu, Hindi, Tamil, Kannada, and natural code-mixed chat.',
    },
    {
      icon: Database,
      title: 'Verified Nutrition Reference',
      desc: 'Grounded in ICMR-NIN Indian Food Composition Tables and USDA FoodData Central data so nutritional values and preparation guidance stay reliable.',
    },
    {
      icon: Wallet,
      title: 'Smart Budget Meal Planning',
      desc: 'Generates dynamic daily, weekly, and monthly meal schedules in ₹ across five meal categories while staying within your stated budget.',
    },
  ];

  return (
    <section className="w-full max-w-5xl mx-auto px-4 sm:px-6 py-10 space-y-10">
      <div className="fg-card p-8 sm:p-10 text-center space-y-4">
        <span className="inline-flex items-center px-3 py-1 rounded-full bg-lavender-mist border border-lavender-border text-royal text-xs font-bold uppercase tracking-wider">
          About FoodGenie
        </span>
        <h1 className="font-display font-extrabold text-3xl sm:text-4xl text-royal tracking-tight">
          Practical, Evidence-Based Nutrition Guidance
        </h1>
        <p className="text-sm sm:text-base text-royal/75 max-w-2xl mx-auto leading-relaxed">
          FoodGenie helps you make healthier everyday food choices with Genie—your AI nutrition companion—combining conversational guidance, structured meal planning, and affordable local wholefoods.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {pillars.map((p) => {
          const Icon = p.icon;
          return (
            <div key={p.title} className="fg-card p-6 space-y-3">
              <div className="w-11 h-11 rounded-2xl bg-royal text-lime-electric flex items-center justify-center">
                <Icon className="w-5 h-5" />
              </div>
              <h2 className="font-display font-bold text-lg text-royal">{p.title}</h2>
              <p className="text-sm text-royal/75 leading-relaxed">{p.desc}</p>
            </div>
          );
        })}
      </div>

      <div className="fg-card p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5">
        <div className="space-y-1.5 max-w-xl">
          <div className="flex items-center gap-2 text-royal font-bold text-sm">
            <ShieldCheck className="w-4 h-4 text-lime-dark" />
            <span>Responsible Nutrition Disclaimer</span>
          </div>
          <p className="text-xs sm:text-sm text-royal/75 leading-relaxed">
            Nutritional figures and retail food prices shown in FoodGenie are estimates for wellness planning and do not replace clinical diagnosis or individualized medical care.
          </p>
        </div>

        <div className="flex flex-wrap gap-2 flex-shrink-0">
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('explore')}
            className="px-4 py-2.5 rounded-xl bg-lavender-mist hover:bg-lavender-dark text-royal text-xs font-bold border border-lavender-border transition-colors"
          >
            Explore Foods
          </button>
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('home')}
            className="px-5 py-2.5 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold flex items-center gap-1.5 transition-colors"
          >
            <span>Chat with Genie</span>
            <ArrowRight className="w-4 h-4 text-lime-electric" />
          </button>
        </div>
      </div>
    </section>
  );
}
