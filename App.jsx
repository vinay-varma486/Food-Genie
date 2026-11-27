import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { Navbar } from './Navbar';
import Home from './Home';
import FoodExplorer from './FoodExplorer';
import About from './About';
import { MoreView } from './MoreView';
import { GoalPlannerView } from './GoalPlannerView';
import { BudgetPlannerView } from './BudgetPlannerView';
import { DoctorFinderView } from './DoctorFinderView';
import { SavedPlansView } from './SavedPlansView';
import { ProfileSettingsView } from './ProfileSettingsView';
import { AuthModal } from './AuthModal';
import { ChatHistoryModal } from './ChatHistoryModal';
import { apiClient } from './api';
import { ErrorBoundary } from './ErrorBoundary';

function getPersistentSessionId() {
  try {
    const existing = localStorage.getItem('foodgenie_session_id');
    if (existing) return existing;
    const created = `session-${Date.now()}`;
    localStorage.setItem('foodgenie_session_id', created);
    return created;
  } catch (_) {
    return `session-${Date.now()}`;
  }
}

export function FoodGenieApp() {
  const { token, isAuthenticated } = useAuth();

  // Navigation: 'home' | 'explore' | 'about' | 'more' | 'goal-gain' | 'goal-loss' | 'goal-maintain' | 'budget' | 'doctors' | 'saved' | 'profile'
  const [currentPage, setCurrentPage] = useState('home');

  // Persistent Chat Session & Messages
  const [sessionId, setSessionId] = useState(getPersistentSessionId);
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatError, setChatError] = useState(null);
  const [lastQuery, setLastQuery] = useState(null);
  const [activeLanguage, setActiveLanguage] = useState('en');

  // Modals
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const navigateTo = (pageId) => {
    setCurrentPage(pageId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNewChat = () => {
    const nextSid = `session-${Date.now()}`;
    setSessionId(nextSid);
    try {
      localStorage.setItem('foodgenie_session_id', nextSid);
    } catch (_) {}
    setMessages([]);
    setChatError(null);
    setLastQuery(null);
  };

  const handleSelectSession = async (pastSessionId) => {
    setSessionId(pastSessionId);
    setChatError(null);
    setIsProcessing(true);
    navigateTo('home');

    try {
      const historyRows = await apiClient.getChatHistory(pastSessionId, token);
      if (Array.isArray(historyRows)) {
        const mapped = [];
        historyRows.forEach((item) => {
          if (item.user_query) {
            mapped.push({
              id: `user-${item.id}`,
              sender: 'user',
              text: item.user_query,
              timestamp: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            });
          }
          if (item.genie_response) {
            mapped.push({
              id: `genie-${item.id}`,
              sender: 'genie',
              text: item.genie_response,
              language: item.language_code || 'en',
              timestamp: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            });
          }
        });
        setMessages(mapped);
      }
    } catch (err) {
      setChatError(err.message || 'Could not load conversation history.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendMessage = async (textToSend, isVoice = false) => {
    const cleanText = (textToSend || '').trim();
    if (!cleanText || isProcessing) return;

    setChatError(null);
    setLastQuery(cleanText);

    // If sending from another page, navigate to home so user sees conversation
    if (currentPage !== 'home') {
      navigateTo('home');
    }

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: cleanText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsProcessing(true);

    try {
      const genieData = await apiClient.getRecommendation(
        cleanText,
        activeLanguage,
        token,
        sessionId,
        isVoice
      );
      if (genieData?.language) {
        setActiveLanguage(genieData.language);
      }

      const summaryText =
        typeof genieData?.summary === 'string' && genieData.summary.trim()
          ? genieData.summary.trim()
          : 'I received your question, please try asking again.';

      const genieMsg = {
        id: `genie-${Date.now()}`,
        sender: 'genie',
        text: summaryText,
        recommendations: genieData?.recommended_foods || [],
        restrictions: genieData?.restrictions || [],
        language: genieData?.language || activeLanguage,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, genieMsg]);
    } catch (err) {
      setChatError(err.message || 'Could not reach FoodGenie server. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F2ECFF] text-[#230852] font-sans">
      {/* Main Top Navigation: Home, Explore Foods, About, More */}
      <Navbar
        currentPage={currentPage}
        onNavigate={navigateTo}
        onOpenAuth={() => setIsAuthOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        <ErrorBoundary onReset={() => navigateTo('home')}>
          {/* 1. HOME: Personalized Greeting + Friendly Genie Chat Interface */}
          {currentPage === 'home' && (
            <Home
              messages={messages}
              isProcessing={isProcessing}
              chatError={chatError}
              activeLanguage={activeLanguage}
              onSendMessage={handleSendMessage}
              onNewChat={handleNewChat}
              onOpenHistory={() => setIsHistoryOpen(true)}
              onRetryLast={lastQuery ? () => handleSendMessage(lastQuery, false) : null}
            />
          )}

          {/* 2. EXPLORE FOODS: Verified ICMR/USDA Catalog with Search & Categories */}
          {currentPage === 'explore' && (
            <FoodExplorer
              onBack={() => navigateTo('home')}
              onAskGenie={(q) => handleSendMessage(q, false)}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {/* 3. ABOUT: Clean Mission, Science & Data Sources */}
          {currentPage === 'about' && (
            <About onNavigate={navigateTo} />
          )}

          {/* 4. MORE: Hub with all 7 Specialized Features */}
          {currentPage === 'more' && (
            <MoreView
              onNavigate={navigateTo}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {/* 4A. Weight Gain Planner */}
          {currentPage === 'goal-gain' && (
            <GoalPlannerView
              initialGoal="weight_gain"
              onBack={() => navigateTo('more')}
              onAskGenie={(q) => handleSendMessage(q, false)}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {/* 4B. Weight Loss Planner */}
          {currentPage === 'goal-loss' && (
            <GoalPlannerView
              initialGoal="weight_loss"
              onBack={() => navigateTo('more')}
              onAskGenie={(q) => handleSendMessage(q, false)}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {/* 4C. Weight Maintenance Planner */}
          {currentPage === 'goal-maintain' && (
            <GoalPlannerView
              initialGoal="maintain_weight"
              onBack={() => navigateTo('more')}
              onAskGenie={(q) => handleSendMessage(q, false)}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {/* 4D. Budget Planner */}
          {currentPage === 'budget' && (
            <BudgetPlannerView
              onBack={() => navigateTo('more')}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {/* 4E. Nearby Doctors */}
          {currentPage === 'doctors' && (
            <DoctorFinderView
              onBack={() => navigateTo('more')}
              onAskGenie={(q) => handleSendMessage(q, false)}
            />
          )}

          {/* 4F. My Saved Plans */}
          {currentPage === 'saved' && (
            <SavedPlansView
              onBack={() => navigateTo('more')}
              onOpenAuth={() => setIsAuthOpen(true)}
              onAskGenie={(q) => handleSendMessage(q, false)}
              onSelectSession={handleSelectSession}
            />
          )}

          {/* 4G. Profile and Settings */}
          {currentPage === 'profile' && (
            <ProfileSettingsView
              onBack={() => navigateTo('more')}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}
        </ErrorBoundary>
      </main>

      {/* Global Modals */}
      <ChatHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        activeSessionId={sessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
      />

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
      />
    </div>
  );
}

export default FoodGenieApp;
