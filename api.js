/**
 * FoodGenie API Client
 * Connects React frontend to FastAPI backend seamlessly in both Vite dev (proxy) and production builds.
 */

const rawEnvUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '';
export const API_BASE_URL = rawEnvUrl ? rawEnvUrl.replace(/\/$/, '') : '/api/v1';

async function parseErrorDetail(res, fallbackMsg) {
  try {
    const body = await res.json();
    if (typeof body?.detail === 'string') return body.detail;
    if (Array.isArray(body?.detail) && body.detail[0]?.msg) return body.detail[0].msg;
    if (body?.message) return body.message;
  } catch (_) {}
  return fallbackMsg || `Request failed (${res.status})`;
}

function buildUrl(endpoint) {
  if (endpoint.startsWith('http')) return endpoint;
  let clean = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  if (clean.startsWith('/api/v1/')) {
    clean = clean.replace(/^\/api\/v1/, '');
  }
  return `${API_BASE_URL}${clean}`;
}

export const apiClient = {
  // Auth
  // Auth & OTP Verification
  async getEmailStatus() {
    const res = await this.get('/auth/email-status');
    return res.data;
  },

  async register(data) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Registration failed'));
    return res.json();
  },

  async verifyOtp(email, otp) {
    const res = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, otp }),
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Invalid or expired OTP'));
    return res.json();
  },

  async resendOtp(email) {
    const res = await fetch(`${API_BASE_URL}/auth/resend-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Could not resend OTP right now'));
    return res.json();
  },

  async login(email, password) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Invalid email or password'));
    return res.json();
  },

  // Genie Recommendations & Conversational AI
  async getRecommendation(query, language = 'en', token = null, sessionId = null, isVoice = false, selectedFood = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE_URL}/recommendations/query`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query,
        language,
        session_id: sessionId,
        is_voice: isVoice,
        selected_food: selectedFood,
      }),
    });
    if (!res.ok) {
      throw new Error(await parseErrorDetail(res, 'Could not reach Genie right now'));
    }
    return await res.json();
  },

  // Budget Diet Planner
  async generateAIBudgetDiet(payload, token = null) {
    const res = await this.post('/budget/ai-plan', payload, token);
    return res.data;
  },

  async saveAIBudgetPlan(plan, token = null) {
    const res = await this.post('/budget/ai-plan/save', plan, token);
    return res.data;
  },

  async getSavedDietPlans(token = null) {
    const res = await this.get('/budget/plans', token);
    return res.data;
  },

  async updateSavedDietPlan(planId, payload, token = null) {
    const res = await this.put(`/budget/plans/${planId}`, payload, token);
    return res.data;
  },

  async deleteSavedDietPlan(planId, token = null) {
    const res = await this.delete(`/budget/plans/${planId}`, token);
    return res.data;
  },

  // Doctors Finder
  async getNearbyDoctors(paramsOrLat, longitude, city = 'Hyderabad', specialization_code = null, language = 'en') {
    const payload = typeof paramsOrLat === 'object' && paramsOrLat !== null
      ? { ...paramsOrLat }
      : {
          latitude: paramsOrLat,
          longitude,
          city: city || 'Hyderabad',
          specialization_code,
          language: language || 'en',
        };
    const res = await fetch(`${API_BASE_URL}/doctors/nearby`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Doctors search failed'));
    return res.json();
  },

  async getDoctorSpecializations(language = 'en') {
    const res = await fetch(`${API_BASE_URL}/doctors/specializations?language=${encodeURIComponent(language)}`);
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Failed to fetch doctor specializations'));
    return res.json();
  },

  // Generic HTTP Helpers
  async post(endpoint, data, token = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(buildUrl(endpoint), {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Request failed'));
    return { data: await res.json() };
  },

  async get(endpoint, token = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(buildUrl(endpoint), { method: 'GET', headers });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Request failed'));
    return { data: await res.json() };
  },

  async put(endpoint, data, token = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(buildUrl(endpoint), {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Request failed'));
    return { data: await res.json() };
  },

  async delete(endpoint, token = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(buildUrl(endpoint), { method: 'DELETE', headers });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Request failed'));
    return { data: await res.json() };
  },

  // User Profile
  async getUserProfile(token) {
    const res = await this.get('/profile/me', token);
    return res.data;
  },

  async updateUserProfile(profileData, token) {
    const res = await this.put('/profile/me', profileData, token);
    return res.data;
  },

  // Chat History
  async getChatHistory(sessionId = null, token = null) {
    const q = sessionId ? `?session_id=${encodeURIComponent(sessionId)}&order=asc` : '?order=asc';
    const res = await this.get(`/chat/history${q}`, token);
    return res.data;
  },

  async getConversations(token = null) {
    const res = await this.get('/chat/conversations', token);
    return res.data;
  },

  async deleteConversation(sessionId, token = null) {
    const res = await this.delete(`/chat/conversations/${encodeURIComponent(sessionId)}`, token);
    return res.data;
  },

  async deleteChatHistory(sessionId = null, token = null) {
    const q = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
    const res = await this.delete(`/chat/history${q}`, token);
    return res.data;
  },

  // Saved Food Recommendations
  async getSavedFoods(token = null) {
    const res = await this.get('/nutrition/saved', token);
    return res.data;
  },

  async saveFood(foodId, notes = '', token = null) {
    const res = await this.post('/nutrition/saved', { food_id: foodId, notes }, token);
    return res.data;
  },

  async deleteSavedFood(foodId, token = null) {
    const res = await this.delete(`/nutrition/saved/${foodId}`, token);
    return res.data;
  },

  // Food Restrictions
  async analyzeRestrictions(payload, token = null) {
    const res = await this.post('/recommendations/restrictions/analyze', payload, token);
    return res.data;
  },

  // Food Items & Nutrition Catalog
  async getFoodItems(query = '', category = null, skip = 0, limit = 50) {
    let url = `/nutrition/foods?skip=${skip}&limit=${limit}`;
    if (query) url += `&query=${encodeURIComponent(query)}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    const res = await this.get(url);
    return res.data;
  },

  // Analytics Dashboard & Meal/Expense Logging
  async getDashboardOverview(
    { dateRange = 'weekly', category = 'all', sessionId = null, search = '', budgetOverride = null } = {},
    token = null
  ) {
    const params = new URLSearchParams({
      date_range: dateRange,
      category: category || 'all',
    });
    if (sessionId) params.set('session_id', sessionId);
    if (search && search.trim()) params.set('search', search.trim());
    if (budgetOverride && Number(budgetOverride) > 0) params.set('budget_override', String(budgetOverride));
    const res = await this.get(`/dashboard/overview?${params.toString()}`, token);
    return res.data;
  },

  async createDashboardLog(payload, token = null) {
    const res = await this.post('/dashboard/logs', payload, token);
    return res.data;
  },

  async deleteDashboardLog(logId, sessionId = null, token = null) {
    const q = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
    const res = await this.delete(`/dashboard/logs/${logId}${q}`, token);
    return res.data;
  },

  async applyCategoryMeals(payload, token = null) {
    const res = await this.post('/dashboard/apply-plan', payload, token);
    return res.data;
  },

  // Grocery & Shopping Basket
  async getGroceryItems(category = null, budgetHeroOnly = false, query = '') {
    const params = new URLSearchParams();
    if (category && category !== 'all') params.set('category', category);
    if (budgetHeroOnly) params.set('budget_hero_only', 'true');
    if (query && query.trim()) params.set('query', query.trim());
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await this.get(`/grocery/items${qs}`);
    return res.data;
  },

  async buildGroceryBasket(payload) {
    const res = await this.post('/grocery/basket', payload);
    return res.data;
  },

  // My Food Cart & Printable PDF Export
  async getMyCart(token) {
    const res = await this.get('/cart', token);
    return res.data;
  },

  async addToCart(payload, token) {
    const res = await this.post('/cart/items', payload, token);
    return res.data;
  },

  async updateCartItem(itemId, payload, token) {
    const res = await this.put(`/cart/items/${itemId}`, payload, token);
    return res.data;
  },

  async removeCartItem(itemId, token) {
    const res = await this.delete(`/cart/items/${itemId}`, token);
    return res.data;
  },

  async clearCart(token) {
    const res = await this.delete('/cart', token);
    return res.data;
  },

  async saveCart(payload, token) {
    const res = await this.post('/cart/save', payload, token);
    return res.data;
  },

  async downloadCartPdf(token) {
    const res = await fetch(`${API_BASE_URL}/cart/pdf`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(await parseErrorDetail(res, 'Failed to generate Food Cart PDF'));
    return res.blob();
  },
};

export const getFoodItems = (params) => apiClient.getFoodItems(params?.query, params?.category, params?.skip, params?.limit);
export const getSavedFoods = (token) => apiClient.getSavedFoods(token);
export const saveFood = (data, token) => apiClient.saveFood(data.food_id, data.notes, token);
export const deleteSavedFood = (foodId, token) => apiClient.deleteSavedFood(foodId, token);
