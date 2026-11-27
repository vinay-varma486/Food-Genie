import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Stethoscope, AlertCircle } from 'lucide-react';

export const FoodRestrictionCard = ({ restriction, onFindDoctor }) => {
  if (!restriction) return null;

  const isMedical = restriction.restriction_type === 'medically_necessary';
  const foodName = restriction.food_name || restriction.name;
  const reason = restriction.reason;
  const alternatives = restriction.safe_alternatives || [];
  const clinicalNote = restriction.clinical_note;
  const category = restriction.category || 'medical_condition';

  const categoryLabels = {
    allergy: 'Food Allergy',
    intolerance: 'Food Intolerance',
    medical_condition: 'Health Condition',
    medication_interaction: 'Medication Interaction',
    dietary_preference: 'Dietary Preference',
  };

  return (
    <div
      className={`rounded-2xl p-4 border ${
        isMedical
          ? 'bg-rose-50/70 border-rose-200'
          : 'bg-amber-50/70 border-amber-200'
      }`}
    >
      <div className="flex flex-wrap items-center gap-2 mb-2">
        {isMedical ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-rose-600 text-white">
            <ShieldAlert className="w-3 h-3" />
            <span>Caution / Avoid</span>
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-amber-600 text-white">
            <AlertCircle className="w-3 h-3" />
            <span>Limit</span>
          </span>
        )}
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white text-royal border border-lavender-border uppercase">
          {categoryLabels[category] || category}
        </span>
      </div>

      <h4 className="font-bold text-sm text-royal mb-1.5">{foodName}</h4>

      <p className="text-xs text-royal/80 leading-relaxed mb-2.5 flex items-start gap-1.5">
        <AlertTriangle className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isMedical ? 'text-rose-600' : 'text-amber-600'}`} />
        <span>{reason}</span>
      </p>

      {alternatives.length > 0 && (
        <div className="mb-2.5">
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-royal/60 flex items-center gap-1 mb-1">
            <CheckCircle2 className="w-3 h-3 text-lime-dark" />
            <span>Suitable Alternatives</span>
          </span>
          <div className="flex flex-wrap gap-1.5">
            {alternatives.map((alt, idx) => (
              <span
                key={idx}
                className="px-2.5 py-0.5 rounded-lg text-xs font-semibold bg-lime-electric/25 text-royal-deep border border-lime-electric/60"
              >
                {alt}
              </span>
            ))}
          </div>
        </div>
      )}

      {clinicalNote && (
        <div className="pt-2 border-t border-royal/10 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-royal/75">
          <div className="flex items-start gap-1.5">
            <Stethoscope className="w-3.5 h-3.5 text-royal flex-shrink-0 mt-0.5" />
            <span>{clinicalNote}</span>
          </div>
          {onFindDoctor && (
            <button
              type="button"
              onClick={onFindDoctor}
              className="px-3 py-1 rounded-lg bg-royal text-white text-[11px] font-bold whitespace-nowrap hover:bg-royal-light"
            >
              Find Doctor
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default FoodRestrictionCard;
