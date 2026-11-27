import React, { useState, useEffect, useCallback } from 'react';
import { apiClient } from './api';
import { useAuth } from './AuthContext';
import { FoodCardDetailed } from './FoodCardDetailed';
import { Search, ArrowLeft, AlertCircle, Loader2, X } from 'lucide-react';

const CATEGORIES = [
  { id: 'all', label: 'All Foods' },
  { id: 'leafy green', label: 'Leafy Greens' },
  { id: 'millet,grain', label: 'Millets & Grains' },
  { id: 'pulse,plant_protein', label: 'Pulses & Legumes' },
  { id: 'fruit,dried_fruit', label: 'Fruits' },
  { id: 'vegetable,tuber', label: 'Vegetables' },
  { id: 'seed,nut', label: 'Seeds & Nuts' },
  { id: 'dairy,poultry', label: 'Dairy & Eggs' },
];

export const FoodExplorer = ({ onBack, onAskGenie, onOpenAuth, onLogFood, onAddToCart, cartFoodIds = new Set() }) => {
  const { token, isAuthenticated } = useAuth();
  const [searchInput, setSearchInput] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [foodItems, setFoodItems] = useState([]);
  const [savedFoodIds, setSavedFoodIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const loadFoods = useCallback(async (queryText, categoryId) => {
    setLoading(true);
    setError(null);
    try {
      const items = await apiClient.getFoodItems(queryText, categoryId, 0, 50);
      setFoodItems(Array.isArray(items) ? items : []);
    } catch (err) {
      setError(err.message || 'Unable to load foods right now. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFoods(activeQuery, selectedCategory);
  }, [activeQuery, selectedCategory, loadFoods]);

  useEffect(() => {
    async function loadSaved() {
      if (!isAuthenticated || !token) {
        setSavedFoodIds(new Set());
        return;
      }
      try {
        const saved = await apiClient.getSavedFoods(token);
        if (Array.isArray(saved)) {
          setSavedFoodIds(new Set(saved.map((s) => s.food_id)));
        }
      } catch (_) {}
    }
    loadSaved();
  }, [isAuthenticated, token]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setActiveQuery(searchInput.trim());
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setActiveQuery('');
    setSelectedCategory('all');
  };

  const handleToggleSave = async (food) => {
    if (!isAuthenticated || !token) {
      if (onOpenAuth) onOpenAuth();
      return;
    }
    setFeedback(null);
    try {
      if (savedFoodIds.has(food.id)) {
        await apiClient.deleteSavedFood(food.id, token);
        setSavedFoodIds((prev) => {
          const next = new Set(prev);
          next.delete(food.id);
          return next;
        });
        setFeedback(`Removed ${food.name} from saved foods.`);
      } else {
        await apiClient.saveFood(food.id, '', token);
        setSavedFoodIds((prev) => new Set([...prev, food.id]));
        setFeedback(`Saved ${food.name} to My Saved Plans.`);
      }
    } catch (err) {
      setError(err.message || 'Could not update saved food.');
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-royal/70 hover:text-royal mb-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Home</span>
            </button>
          )}
          <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-royal tracking-tight">
            Explore Verified Foods
          </h1>
          <p className="text-xs sm:text-sm text-royal/70 mt-0.5">
            Search wholefoods, macros, vitamins, minerals, and preparation tips (ICMR-NIN &amp; USDA data)
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-72">
            <Search className="w-4 h-4 text-royal/45 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search spinach, ragi, protein..."
              className="w-full pl-10 pr-8 py-2.5 rounded-xl bg-white border border-lavender-border text-sm text-royal placeholder:text-royal/45 focus:outline-none focus:border-royal"
            />
            {searchInput && (
              <button
                type="button"
                onClick={handleClearSearch}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-royal/45 hover:text-royal"
                aria-label="Clear search"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2.5 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold shadow-xs disabled:opacity-60"
          >
            Search
          </button>
        </form>
      </div>

      {/* Category Filter Buttons */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {CATEGORIES.map((cat) => {
          const active = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3.5 py-2 rounded-full text-xs font-bold whitespace-nowrap border transition-colors ${
                active
                  ? 'bg-royal text-white border-royal shadow-xs'
                  : 'bg-white hover:bg-lavender-light text-royal/80 border-lavender-border'
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {feedback && (
        <div className="px-4 py-2.5 rounded-xl bg-lime-electric/25 border border-lime-electric text-xs font-bold text-royal-deep">
          {feedback}
        </div>
      )}

      {error && (
        <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center justify-between gap-3">
          <span className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </span>
          <button
            type="button"
            onClick={() => loadFoods(activeQuery, selectedCategory)}
            className="px-3 py-1 rounded-lg bg-red-600 text-white font-bold"
          >
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-royal/70 gap-2">
          <Loader2 className="w-7 h-7 animate-spin text-royal" />
          <p className="text-xs font-semibold">Loading verified nutrition catalog...</p>
        </div>
      ) : foodItems.length === 0 ? (
        <div className="fg-card p-10 text-center space-y-3">
          <p className="font-bold text-base text-royal">No foods matched your search</p>
          <p className="text-xs text-royal/65">
            Try another keyword or clear your filters to browse all verified foods.
          </p>
          <button
            type="button"
            onClick={handleClearSearch}
            className="px-4 py-2 rounded-xl bg-royal text-white text-xs font-bold"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {foodItems.map((food) => (
            <FoodCardDetailed
              key={food.id}
              food={food}
              isInCart={cartFoodIds.has(food.id)}
              onAddToCart={onAddToCart}
              onLogFood={onLogFood}
              onAskGenie={(q, f) => onAskGenie && onAskGenie(q, f)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default FoodExplorer;
