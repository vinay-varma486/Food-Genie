import React, { useState } from 'react';
import {
  Utensils, HeartPulse, ChevronDown, ChevronUp, Scale,
  ShoppingCart, Check, MessageSquare, AlertTriangle, Plus
} from 'lucide-react';

export const FoodCardDetailed = ({
  food,
  language = 'en',
  isInCart = false,
  onAddToCart,
  onLogFood,
  onAskGenie,
}) => {
  const [portionMode, setPortionMode] = useState('serving'); // 'serving' | '100g'
  const [showPrepTips, setShowPrepTips] = useState(false);
  const [addingCart, setAddingCart] = useState(false);

  const macros = portionMode === 'serving' && food.nutrients_per_serving
    ? food.nutrients_per_serving
    : (food.nutrients_per_100g || {
        calories_kcal: food.calories_kcal || 0,
        protein_g: food.protein_g || 0,
        carbs_g: food.carbs_g || 0,
        fat_g: food.fat_g || 0,
        fiber_g: food.fiber_g || 0,
      });

  const servingLabel = portionMode === 'serving'
    ? (food.serving_size || '1 serving (100g)')
    : 'Per 100g';

  const benefitText = food.benefit || food.benefits_summary || 'Nutritious wholefood supporting daily balance.';
  const prepText = food.how_to_consume || food.preparation_methods;

  const vitamins = food.vitamins?.length
    ? food.vitamins
    : (food.nutrients?.filter((n) => n.nutrient_category === 'vitamin') || []);
  const minerals = food.minerals?.length
    ? food.minerals
    : (food.nutrients?.filter((n) => n.nutrient_category === 'mineral' || n.nutrient_category === 'essential_fatty_acid') || []);

  const handleAddCart = async () => {
    if (!onAddToCart || addingCart) return;
    setAddingCart(true);
    try {
      await onAddToCart(food);
    } finally {
      setAddingCart(false);
    }
  };

  return (
    <div className="fg-card p-4 sm:p-5 flex flex-col justify-between gap-3">
      <div className="space-y-3">
        {/* Top Row: Category + Portion Toggle */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 flex-wrap">
            {food.category && (
              <span className="px-2.5 py-0.5 rounded-full bg-[#F2ECFF] text-[#351078] border border-[#D8C5FF] text-[10px] font-extrabold uppercase tracking-wider">
                {food.category.replace('_', ' ')}
              </span>
            )}
            {food.meal_category && (
              <span className="px-2.5 py-0.5 rounded-full bg-[#EEF8FC] text-[#230852] border border-[#ADD8E6] text-[10px] font-bold">
                {food.meal_category}
              </span>
            )}
          </div>

          <div className="inline-flex bg-[#F2ECFF] p-0.5 rounded-full border border-[#D8C5FF] text-[10px] font-bold">
            <button
              type="button"
              onClick={() => setPortionMode('serving')}
              className={`px-2.5 py-0.5 rounded-full transition-colors ${
                portionMode === 'serving' ? 'bg-[#351078] text-white' : 'text-[#5B4B7A] hover:text-[#351078]'
              }`}
            >
              Serving
            </button>
            <button
              type="button"
              onClick={() => setPortionMode('100g')}
              className={`px-2.5 py-0.5 rounded-full transition-colors ${
                portionMode === '100g' ? 'bg-[#351078] text-white' : 'text-[#5B4B7A] hover:text-[#351078]'
              }`}
            >
              100g
            </button>
          </div>
        </div>

        {/* Food Name & Regional Titles */}
        <div>
          <h4 className="font-display font-extrabold text-base text-[#230852] leading-snug">
            {food.name}
          </h4>
          {(food.name_te || food.name_hi) && (
            <p className="text-xs text-[#5B4B7A] font-medium mt-0.5">
              {language === 'te'
                ? food.name_te
                : language === 'hi'
                ? food.name_hi
                : [food.name_te, food.name_hi].filter(Boolean).join(' • ')}
            </p>
          )}
        </div>

        {/* Quantity & Estimated Price Row */}
        <div className="flex items-center justify-between text-xs bg-[#EEF8FC] px-3 py-2 rounded-xl border border-[#ADD8E6]">
          <span className="flex items-center gap-1.5 text-[#230852] font-semibold">
            <Scale className="w-3.5 h-3.5 text-[#351078]" />
            <span>{servingLabel}</span>
          </span>
          {food.estimated_price_inr !== undefined && (
            <span className="font-extrabold text-[#351078]">
              ~₹{Math.round(food.estimated_price_inr)} <span className="text-[10px] font-medium text-[#5B4B7A]">(est.)</span>
            </span>
          )}
        </div>

        {/* Macros Grid (Calories, Protein, Carbs, Fats) */}
        <div className="grid grid-cols-4 gap-1.5 text-center">
          <div className="bg-[#FAF7FF] p-2 rounded-xl border border-[#E5DAFB]">
            <span className="block text-[9px] uppercase font-bold text-[#5B4B7A]">Calories</span>
            <span className="font-extrabold text-xs text-[#230852]">{Math.round(macros.calories_kcal || 0)}</span>
            <span className="block text-[9px] text-[#5B4B7A]">kcal</span>
          </div>
          <div className="bg-[#EEF8FC] p-2 rounded-xl border border-[#ADD8E6]">
            <span className="block text-[9px] uppercase font-bold text-[#351078]">Protein</span>
            <span className="font-extrabold text-xs text-[#230852]">{Number(macros.protein_g || 0).toFixed(1)}g</span>
          </div>
          <div className="bg-[#FAF7FF] p-2 rounded-xl border border-[#E5DAFB]">
            <span className="block text-[9px] uppercase font-bold text-[#5B4B7A]">Carbs</span>
            <span className="font-extrabold text-xs text-[#230852]">{Number(macros.carbs_g || 0).toFixed(1)}g</span>
          </div>
          <div className="bg-[#FAF7FF] p-2 rounded-xl border border-[#E5DAFB]">
            <span className="block text-[9px] uppercase font-bold text-[#5B4B7A]">Fats</span>
            <span className="font-extrabold text-xs text-[#230852]">{Number(macros.fat_g || 0).toFixed(1)}g</span>
          </div>
        </div>

        {/* Health Benefits */}
        <div>
          <h5 className="text-[11px] font-extrabold uppercase tracking-wider text-[#5B4B7A] mb-1 flex items-center gap-1">
            <HeartPulse className="w-3.5 h-3.5 text-[#16A34A]" />
            <span>Health Benefits</span>
          </h5>
          <p className="text-xs text-[#230852]/85 leading-relaxed line-clamp-3">{benefitText}</p>
        </div>

        {/* Important Vitamins & Minerals */}
        {(vitamins.length > 0 || minerals.length > 0) && (
          <div className="bg-[#FAF7FF] p-3 rounded-xl border border-[#E5DAFB] space-y-1.5">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-[#5B4B7A] block">
              Vitamins &amp; Minerals ({portionMode === 'serving' ? 'Per Serving' : 'Per 100g'})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {[...vitamins.slice(0, 3), ...minerals.slice(0, 3)].map((n, i) => {
                const name = n.name || n.nutrient_name;
                const val = portionMode === 'serving' && n.amount_per_serving !== undefined
                  ? n.amount_per_serving
                  : n.amount_per_100g;
                return (
                  <span
                    key={`${name}-${i}`}
                    className="px-2 py-0.5 rounded-lg bg-white border border-[#ADD8E6] text-[11px] font-semibold text-[#351078]"
                  >
                    {name}: <strong>{val}{n.unit}</strong>
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Cautions */}
        {food.cautions && (
          <p className="text-[11px] text-amber-900 bg-amber-50 border border-amber-200 rounded-xl px-3 py-1.5 flex items-start gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
            <span>{food.cautions}</span>
          </p>
        )}

        {/* Preparation Instructions */}
        {prepText && (
          <div className="border border-[#E5DAFB] rounded-xl overflow-hidden bg-[#FAF7FF]">
            <button
              type="button"
              onClick={() => setShowPrepTips((s) => !s)}
              className="w-full px-3 py-2 text-left flex items-center justify-between text-xs font-bold text-[#351078] hover:bg-[#F2ECFF] transition-colors"
            >
              <span className="flex items-center gap-1.5">
                <Utensils className="w-3.5 h-3.5 text-[#351078]" />
                <span>Preparation Instructions</span>
              </span>
              {showPrepTips ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            {showPrepTips && (
              <div className="px-3 py-2.5 text-xs text-[#230852] leading-relaxed border-t border-[#E5DAFB] bg-white">
                {prepText}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Actions & Add to My Food Cart */}
      <div className="pt-2 border-t border-[#F2ECFF] space-y-2">
        {onAddToCart && (
          <button
            type="button"
            onClick={handleAddCart}
            disabled={addingCart}
            className={`w-full py-2.5 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-colors ${
              isInCart
                ? 'bg-[#C6FF00] hover:bg-[#B5EA00] text-[#230852]'
                : 'bg-[#351078] hover:bg-[#4C18AB] text-white'
            }`}
          >
            {isInCart ? <Check className="w-3.5 h-3.5" /> : <ShoppingCart className="w-3.5 h-3.5 text-[#C6FF00]" />}
            <span>
              {addingCart
                ? 'Adding to Cart...'
                : isInCart
                ? 'In Food Cart (+ Add Another)'
                : 'Add to My Food Cart'}
            </span>
          </button>
        )}

        {(onLogFood || onAskGenie) && (
          <div className="flex items-center gap-1.5">
            {onLogFood && food.id && (
              <button
                type="button"
                onClick={() => onLogFood(food)}
                className="flex-1 py-2 px-2.5 rounded-xl bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#230852] border border-[#ADD8E6] text-xs font-bold flex items-center justify-center gap-1 transition-colors"
              >
                <Plus className="w-3.5 h-3.5 text-[#351078]" />
                <span>Log Intake</span>
              </button>
            )}
            {onAskGenie && (
              <button
                type="button"
                onClick={() =>
                  onAskGenie(
                    `Analyze ${food.name} (${food.serving_size || '100g'}): is it suitable for my goals, nutritional benefits, and any cheaper alternatives?`,
                    food
                  )
                }
                className="flex-1 py-2 px-2.5 rounded-xl bg-white hover:bg-[#F2ECFF] text-[#351078] border border-[#D8C5FF] text-xs font-bold flex items-center justify-center gap-1 transition-colors"
              >
                <MessageSquare className="w-3.5 h-3.5 text-[#351078]" />
                <span>Ask Genie</span>
              </button>
            )}
          </div>
        )}
        <p className="text-[10px] text-[#5B4B7A] truncate">
          Ref: {food.verified_source || 'ICMR-NIN / USDA FoodData Central'}
        </p>
      </div>
    </div>
  );
};

export default FoodCardDetailed;
