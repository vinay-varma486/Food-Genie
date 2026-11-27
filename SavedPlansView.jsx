import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { apiClient } from './api';
import {
  ArrowLeft, Bookmark, Heart, MessageSquare, Trash2, Edit2,
  Check, X, Loader2, AlertCircle, LogIn
} from 'lucide-react';

export const SavedPlansView = ({
  onBack,
  onOpenAuth,
  onAskGenie,
  onSelectSession,
}) => {
  const { token, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('plans'); // 'plans' | 'foods' | 'chats'
  const [plans, setPlans] = useState([]);
  const [savedFoods, setSavedFoods] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [editingPlanId, setEditingPlanId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [expandedPlanId, setExpandedPlanId] = useState(null);

  const loadAll = useCallback(async () => {
    if (!isAuthenticated || !token) return;
    setLoading(true);
    setError(null);
    try {
      const [p, f, c] = await Promise.all([
        apiClient.getSavedDietPlans(token),
        apiClient.getSavedFoods(token),
        apiClient.getConversations(token),
      ]);
      setPlans(Array.isArray(p) ? p : []);
      setSavedFoods(Array.isArray(f) ? f : []);
      setConversations(Array.isArray(c) ? c : []);
    } catch (err) {
      setError(err.message || 'Could not load your saved items.');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, token]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleDeletePlan = async (planId) => {
    try {
      await apiClient.deleteSavedDietPlan(planId, token);
      setPlans((prev) => prev.filter((p) => p.id !== planId));
    } catch (err) {
      setError(err.message || 'Failed to delete plan.');
    }
  };

  const handleRenamePlan = async (planId) => {
    if (!editingTitle.trim()) return;
    try {
      await apiClient.updateSavedDietPlan(planId, { title: editingTitle.trim() }, token);
      setPlans((prev) => prev.map((p) => (p.id === planId ? { ...p, title: editingTitle.trim() } : p)));
      setEditingPlanId(null);
    } catch (err) {
      setError(err.message || 'Failed to update plan title.');
    }
  };

  const handleDeleteFood = async (foodId) => {
    try {
      await apiClient.deleteSavedFood(foodId, token);
      setSavedFoods((prev) => prev.filter((f) => f.food_id !== foodId));
    } catch (err) {
      setError(err.message || 'Failed to remove saved food.');
    }
  };

  const handleDeleteChat = async (sessionId) => {
    try {
      await apiClient.deleteConversation(sessionId, token);
      setConversations((prev) => prev.filter((c) => c.session_id !== sessionId));
    } catch (err) {
      setError(err.message || 'Failed to delete conversation.');
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div>
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-royal/70 hover:text-royal mb-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>
        <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-royal">
          My Saved Plans
        </h1>
        <p className="text-xs sm:text-sm text-royal/70">
          Review, edit, or manage your saved diet plans, food recommendations, and chat history
        </p>
      </div>

      {!isAuthenticated ? (
        <div className="fg-card p-8 text-center space-y-3">
          <p className="font-bold text-base text-royal">Sign in to view your saved plans</p>
          <p className="text-xs text-royal/70 max-w-md mx-auto">
            Create an account or sign in with your email and password to keep your budget plans, saved foods, and conversations across sessions.
          </p>
          <button
            type="button"
            onClick={onOpenAuth}
            className="px-5 py-2.5 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold inline-flex items-center gap-2"
          >
            <LogIn className="w-4 h-4 text-lime-electric" />
            <span>Sign In / Register</span>
          </button>
        </div>
      ) : (
        <>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {[
              { id: 'plans', label: `Saved Diet Plans (${plans.length})`, icon: Bookmark },
              { id: 'foods', label: `Saved Foods (${savedFoods.length})`, icon: Heart },
              { id: 'chats', label: `Conversations (${conversations.length})`, icon: MessageSquare },
            ].map((t) => {
              const Icon = t.icon;
              return (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setActiveTab(t.id)}
                  className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 whitespace-nowrap border ${
                    activeTab === t.id
                      ? 'bg-royal text-white border-royal'
                      : 'bg-white text-royal/80 border-lavender-border hover:bg-lavender-light'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>

          {error && (
            <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {loading ? (
            <div className="py-12 flex items-center justify-center gap-2 text-xs font-bold text-royal">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Loading your saved items...</span>
            </div>
          ) : activeTab === 'plans' ? (
            plans.length === 0 ? (
              <div className="fg-card p-8 text-center text-xs text-royal/70">
                No saved diet plans yet. Create one in Budget Planner or a Goal Planner and click &quot;Save Plan&quot;.
              </div>
            ) : (
              <div className="space-y-4">
                {plans.map((p) => {
                  const isExpanded = expandedPlanId === p.id;
                  const days = Array.isArray(p.meals_plan_data) ? p.meals_plan_data : [];
                  return (
                    <div key={p.id} className="fg-card p-5 space-y-3">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        {editingPlanId === p.id ? (
                          <div className="flex items-center gap-2 flex-1">
                            <input
                              type="text"
                              value={editingTitle}
                              onChange={(e) => setEditingTitle(e.target.value)}
                              className="flex-1 px-3 py-1.5 rounded-lg bg-lavender-light border border-lavender-border text-sm font-bold text-royal"
                            />
                            <button
                              type="button"
                              onClick={() => handleRenamePlan(p.id)}
                              className="p-1.5 rounded-lg bg-royal text-white"
                              aria-label="Save title"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => setEditingPlanId(null)}
                              className="p-1.5 rounded-lg bg-lavender-mist text-royal"
                              aria-label="Cancel"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <div>
                            <h3 className="font-bold text-base text-royal">{p.title}</h3>
                            <p className="text-xs text-royal/65">
                              {p.duration_type} • Est. ₹{p.estimated_cost_inr} • ~{p.target_calories_daily} kcal/day
                            </p>
                          </div>
                        )}

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => setExpandedPlanId(isExpanded ? null : p.id)}
                            className="px-3 py-1.5 rounded-lg bg-lavender-mist text-royal text-xs font-bold"
                          >
                            {isExpanded ? 'Hide Meals' : 'View Meals'}
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setEditingPlanId(p.id);
                              setEditingTitle(p.title);
                            }}
                            className="p-2 rounded-lg hover:bg-lavender-mist text-royal/70"
                            title="Rename plan"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeletePlan(p.id)}
                            className="p-2 rounded-lg hover:bg-red-50 text-red-600"
                            title="Delete plan"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {isExpanded && days.length > 0 && (
                        <div className="pt-3 border-t border-lavender-mist space-y-2">
                          {days.slice(0, 7).map((d, di) => (
                            <div key={di} className="p-3 rounded-xl bg-lavender-light border border-lavender-border text-xs">
                              <div className="flex justify-between font-bold text-royal mb-1">
                                <span>{d.day_label}</span>
                                <span>₹{d.daily_cost_inr}</span>
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-royal/80">
                                {Object.values(d.meals || {}).map((m, mi) => (
                                  <span key={mi}>
                                    <strong>{m.meal_label}:</strong> {m.food_name}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )
          ) : activeTab === 'foods' ? (
            savedFoods.length === 0 ? (
              <div className="fg-card p-8 text-center text-xs text-royal/70">
                No saved foods yet. Bookmark foods in Explore Foods or Genie recommendations.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {savedFoods.map((f) => (
                  <div key={f.food_id} className="fg-card p-4 flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <h3 className="font-bold text-sm text-royal truncate">{f.food_name}</h3>
                      <p className="text-xs text-royal/65 truncate">{f.benefits_summary}</p>
                      <p className="text-[11px] font-semibold text-royal/75 mt-1">
                        {f.calories_kcal} kcal • {f.protein_g}g protein (per 100g)
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      {onAskGenie && (
                        <button
                          type="button"
                          onClick={() => onAskGenie(`Tell me more about ${f.food_name} and healthy recipes.`)}
                          className="px-3 py-1.5 rounded-lg bg-royal text-white text-xs font-bold"
                        >
                          Ask Genie
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => handleDeleteFood(f.food_id)}
                        className="p-2 rounded-lg hover:bg-red-50 text-red-600"
                        title="Remove saved food"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : conversations.length === 0 ? (
            <div className="fg-card p-8 text-center text-xs text-royal/70">
              No saved conversations yet. Start chatting with Genie on the Home page!
            </div>
          ) : (
            <div className="space-y-3">
              {conversations.map((c) => (
                <div key={c.session_id} className="fg-card p-4 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="font-bold text-sm text-royal truncate">{c.title}</h3>
                    <p className="text-xs text-royal/65">
                      {c.message_count} messages • {new Date(c.last_active || c.started_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {onSelectSession && (
                      <button
                        type="button"
                        onClick={() => onSelectSession(c.session_id)}
                        className="px-3 py-1.5 rounded-lg bg-royal text-white text-xs font-bold"
                      >
                        Open Chat
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleDeleteChat(c.session_id)}
                      className="p-2 rounded-lg hover:bg-red-50 text-red-600"
                      title="Delete conversation"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SavedPlansView;

