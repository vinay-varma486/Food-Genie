import React from 'react';
import { useAuth } from './AuthContext';
import { MainChatArea } from './MainChatArea';
import { BottomChatInput } from './BottomChatInput';
import { Sparkles, Plus, History, AlertCircle } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  { label: 'Suggest healthy breakfast', query: 'Suggest healthy breakfast options' },
  { label: 'Hair fall nutrition', query: 'I am experiencing hair fall. What foods should I eat?' },
  { label: 'Clear skin guidance', query: 'I want clear skin. What foods support healthy skin?' },
  { label: 'Weight gain plan', query: 'I want to gain weight.' },
  { label: 'Weight loss plan', query: 'I want to lose weight with a healthy diet.' },
  { label: 'Iron-rich foods', query: 'What foods are rich in iron?' },
  { label: 'Budget plan under ₹150/day', query: 'Create a budget-friendly diet plan under ₹150 per day' },
  { label: 'Vegetarian protein', query: 'Suggest high protein vegetarian foods for daily meals' },
];

export default function Home({
  messages = [],
  isProcessing = false,
  chatError = null,
  activeLanguage = 'en',
  onSendMessage,
  onNewChat,
  onOpenHistory,
  onAddToCart,
  onLogFood,
  cartFoodIds,
  onRetryLast,
}) {
  const { displayName } = useAuth();

  return (
    <main className="w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      {/* Personalized Greeting & Welcome */}
      <section className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EEF8FC] border border-[#ADD8E6] text-[#351078] text-xs font-bold">
          <Sparkles className="w-3.5 h-3.5 text-[#351078]" />
          <span>Genie AI Nutritionist • ICMR-NIN &amp; USDA Verified</span>
        </div>
        <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-[#351078] tracking-tight">
          Hello, {displayName}!
        </h1>
        <p className="text-xs sm:text-sm text-[#5B4B7A] leading-relaxed max-w-2xl">
          Welcome to FoodGenie! I'm Genie, your personal AI nutrition companion. How can I assist you with your diet and health goals today?
        </p>
      </section>

      {/* Main Genie Chat Interface */}
      <section className="fg-card p-4 sm:p-6 space-y-4">
        <div className="flex items-center justify-between gap-3 pb-3 border-b border-[#F2ECFF] flex-wrap">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-[#351078] text-[#C6FF00] flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-display font-bold text-sm sm:text-base text-[#230852]">
                Chat with Genie AI
              </h2>
              <p className="text-[11px] text-[#5B4B7A]">
                Automatic multilingual intelligence • Grounded nutrition tables • Smart budget plans
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {onOpenHistory && (
              <button
                type="button"
                onClick={onOpenHistory}
                className="px-3 py-1.5 rounded-xl bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#351078] text-xs font-bold border border-[#ADD8E6] flex items-center gap-1.5 transition-colors"
                title="View previous chats"
              >
                <History className="w-3.5 h-3.5" />
                <span>History</span>
              </button>
            )}
            {messages.length > 0 && onNewChat && (
              <button
                type="button"
                onClick={onNewChat}
                className="px-3 py-1.5 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center gap-1.5 transition-colors"
                title="Start a fresh conversation"
              >
                <Plus className="w-3.5 h-3.5 text-[#C6FF00]" />
                <span>New Chat</span>
              </button>
            )}
          </div>
        </div>

        {/* Empty State: Welcome Card + Suggested Questions */}
        {messages.length === 0 && (
          <div className="bg-[#F2ECFF]/60 rounded-2xl p-4 sm:p-5 border border-[#D8C5FF] space-y-4">
            <p className="text-sm text-[#230852] leading-relaxed">
              Ask me anything about healthy meals, symptoms (like hair fall or clear skin), weight gain/loss diet plans, or ask for budget-friendly foods in ₹. I understand English, Telugu, Hindi, Tamil, and Kannada automatically!
            </p>

            <div className="space-y-2">
              <p className="text-[11px] font-extrabold uppercase tracking-wider text-[#5B4B7A]">
                Suggested Questions
              </p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_QUESTIONS.map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    onClick={() => onSendMessage && onSendMessage(item.query, false)}
                    disabled={isProcessing}
                    className="px-3.5 py-2 rounded-xl bg-white hover:bg-[#351078] hover:text-white text-[#351078] text-xs font-semibold border border-[#D8C5FF] transition-colors disabled:opacity-50"
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Message Stream */}
        <MainChatArea
          messages={messages}
          isProcessing={isProcessing}
          onAskGenie={(q, f) => onSendMessage && onSendMessage(q, false, f)}
          onAddToCart={onAddToCart}
          onLogFood={onLogFood}
          cartFoodIds={cartFoodIds}
        />

        {/* Error Notification */}
        {chatError && (
          <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800 flex items-center justify-between gap-3">
            <span className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-600" />
              <span>{chatError}</span>
            </span>
            {onRetryLast && (
              <button
                type="button"
                onClick={onRetryLast}
                className="px-3 py-1 rounded-lg bg-red-600 text-white font-bold flex-shrink-0"
              >
                Retry
              </button>
            )}
          </div>
        )}

        {/* Query Input with Microphone & Send Button */}
        <BottomChatInput
          onSendMessage={onSendMessage}
          isProcessing={isProcessing}
          activeLanguage={activeLanguage}
        />
      </section>
    </main>
  );
}
