import React, { useState, useRef, useEffect } from 'react';
import {
  Sparkles,
  X,
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  ShoppingCart,
  Plus,
  Loader2,
  MessageSquare,
} from 'lucide-react';
import { useAuth } from './AuthContext';
import { GenieFormattedResponse } from './MainChatArea';

const SPEECH_LANG_MAP = {
  en: 'en-IN',
  te: 'te-IN',
  hi: 'hi-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
};

export const FloatingGenieChat = ({
  isOpen = false,
  onToggle,
  messages = [],
  isProcessing = false,
  chatError = null,
  activeLanguage = 'en',
  onSendMessage,
  onAddToCart,
  cartCount = 0,
  selectedFood = null,
  onClearSelectedFood,
}) => {
  const { displayName } = useAuth();
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  const [speakingId, setSpeakingId] = useState(null);
  const endRef = useRef(null);
  const recognitionRef = useRef(null);

  const SpeechRecognition =
    typeof window !== 'undefined'
      ? window.SpeechRecognition || window.webkitSpeechRecognition
      : null;
  const isVoiceSupported = Boolean(SpeechRecognition);
  const isTtsSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  useEffect(() => {
    if (isOpen) {
      endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [isOpen, messages.length, isProcessing]);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (_) {}
      }
      if (isTtsSupported) {
        try { window.speechSynthesis.cancel(); } catch (_) {}
      }
    };
  }, [isTtsSupported]);

  const handleSend = (overrideText = null, viaVoice = false) => {
    const clean = (overrideText !== null ? overrideText : input).trim();
    if (!clean || isProcessing) return;
    setVoiceError(null);
    if (onSendMessage) {
      onSendMessage(clean, viaVoice, selectedFood);
    }
    if (overrideText === null) setInput('');
  };

  const toggleVoice = () => {
    if (!SpeechRecognition || isProcessing) return;
    setVoiceError(null);
    if (isListening && recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (_) {}
      setIsListening(false);
      return;
    }
    try {
      const rec = new SpeechRecognition();
      rec.lang = SPEECH_LANG_MAP[activeLanguage] || 'en-IN';
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      rec.onstart = () => setIsListening(true);
      rec.onresult = (ev) => {
        const t = ev.results?.[0]?.[0]?.transcript?.trim();
        if (t) setInput((prev) => (prev ? `${prev} ${t}` : t));
      };
      rec.onerror = () => {
        setIsListening(false);
        setVoiceError('Microphone unavailable. Please type your message.');
      };
      rec.onend = () => setIsListening(false);
      recognitionRef.current = rec;
      rec.start();
    } catch (_) {
      setIsListening(false);
      setVoiceError('Could not start voice input.');
    }
  };

  const toggleSpeak = (msg) => {
    if (!isTtsSupported) return;
    if (speakingId === msg.id) {
      window.speechSynthesis.cancel();
      setSpeakingId(null);
      return;
    }
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(
      (msg.text || '').replace(/\|[^\n]+\|/g, ' ').replace(/[#*_`]/g, '').slice(0, 600)
    );
    utt.lang = SPEECH_LANG_MAP[msg.language] || 'en-IN';
    utt.onend = () => setSpeakingId(null);
    utt.onerror = () => setSpeakingId(null);
    setSpeakingId(msg.id);
    window.speechSynthesis.speak(utt);
  };

  const quickChips = [
    { label: 'Analyze my cart', query: 'Analyze my Food Cart calories, protein, and budget.' },
    { label: 'Cheaper alternatives', query: 'Suggest cheaper nutritious alternatives.' },
    { label: 'Good for weight gain?', query: selectedFood ? `Is ${selectedFood.name} good for weight gain?` : 'Which foods in our database are best for healthy weight gain?' },
  ];

  return (
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end gap-3">
      {/* Compact Floating Chat Panel */}
      {isOpen && (
        <div className="w-[calc(100vw-2rem)] sm:w-[390px] h-[510px] max-h-[78vh] bg-white rounded-2xl border border-[#D8C5FF] shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-[#351078] text-white px-4 py-3 flex items-center justify-between gap-2 flex-shrink-0">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-xl bg-[#230852] border border-[#C6FF00]/40 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-4 h-4 text-[#C6FF00]" />
              </div>
              <div className="min-w-0">
                <p className="font-display font-bold text-sm truncate">Genie AI Assistant</p>
                <p className="text-[10px] text-[#E5DAFB] truncate">
                  Hello, {displayName} • Cart-aware ({cartCount} items)
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={onToggle}
              className="p-1.5 rounded-lg hover:bg-white/10 text-white"
              aria-label="Close Genie chat"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Active Selected Food Context Pill */}
          {selectedFood && (
            <div className="px-3.5 py-2 bg-[#EEF8FC] border-b border-[#ADD8E6] flex items-center justify-between gap-2 text-[11px] text-[#230852]">
              <span className="truncate font-semibold">
                Context: <strong>{selectedFood.name}</strong> ({selectedFood.calories_kcal || 0} kcal)
              </span>
              {onClearSelectedFood && (
                <button
                  type="button"
                  onClick={onClearSelectedFood}
                  className="text-[#351078] hover:underline font-bold flex-shrink-0"
                >
                  Clear
                </button>
              )}
            </div>
          )}

          {/* Conversation Stream */}
          <div className="flex-1 overflow-y-auto p-3.5 space-y-3 bg-[#FAF7FF]">
            {messages.length === 0 ? (
              <div className="space-y-3">
                <div className="p-3.5 rounded-2xl bg-white border border-[#D8C5FF] text-xs text-[#230852] leading-relaxed">
                  Hi <strong>{displayName}</strong>! Ask me nutrition questions, compare prices, check your saved Food Cart ({cartCount} items), or request cheaper wholefood swaps.
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {quickChips.map((chip) => (
                    <button
                      key={chip.label}
                      type="button"
                      onClick={() => handleSend(chip.query, false)}
                      disabled={isProcessing}
                      className="px-2.5 py-1.5 rounded-xl bg-[#EEF8FC] hover:bg-[#351078] hover:text-white text-[#351078] border border-[#ADD8E6] text-[11px] font-bold transition-colors"
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => {
                const isUser = msg.sender === 'user';
                const recs = msg.recommendations || [];
                return (
                  <div key={msg.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`max-w-[90%] rounded-2xl p-3 text-xs ${
                        isUser
                          ? 'bg-[#351078] text-white rounded-br-sm'
                          : 'bg-white border border-[#D8C5FF] text-[#230852] rounded-bl-sm'
                      }`}
                    >
                      {!isUser && isTtsSupported && msg.text && (
                        <div className="flex justify-end mb-1">
                          <button
                            type="button"
                            onClick={() => toggleSpeak(msg)}
                            className="inline-flex items-center gap-1 text-[10px] font-bold text-[#351078] hover:underline"
                          >
                            {speakingId === msg.id ? <VolumeX className="w-3 h-3 text-red-600" /> : <Volume2 className="w-3 h-3" />}
                            <span>{speakingId === msg.id ? 'Stop' : 'Listen'}</span>
                          </button>
                        </div>
                      )}

                      {isUser ? (
                        <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                      ) : (
                        <GenieFormattedResponse content={msg.text} />
                      )}

                      {recs.length > 0 && onAddToCart && (
                        <div className="mt-2 pt-2 border-t border-[#F2ECFF] space-y-1.5">
                          <p className="text-[10px] font-extrabold uppercase text-[#351078]">
                            Quick Add Recommended Foods
                          </p>
                          {recs.slice(0, 3).map((item, idx) => (
                            <div
                              key={item.id || idx}
                              className="flex items-center justify-between gap-2 p-2 rounded-xl bg-[#EEF8FC] border border-[#ADD8E6]"
                            >
                              <div className="min-w-0">
                                <p className="font-bold text-[11px] text-[#230852] truncate">{item.name}</p>
                                <p className="text-[10px] text-[#5B4B7A]">
                                  ₹{Math.round(item.estimated_price_inr || 15)} • {item.serving_size}
                                </p>
                              </div>
                              <button
                                type="button"
                                onClick={() => onAddToCart(item)}
                                className="px-2 py-1 rounded-lg bg-[#351078] text-white text-[10px] font-bold flex items-center gap-1 flex-shrink-0"
                              >
                                <ShoppingCart className="w-3 h-3 text-[#C6FF00]" />
                                <span>Add</span>
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}

            {isProcessing && (
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-[#EEF8FC] border border-[#ADD8E6] w-fit text-[11px] font-bold text-[#351078]">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Genie is thinking...</span>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Input Footer */}
          <div className="p-2.5 bg-white border-t border-[#E5DAFB] space-y-1.5 flex-shrink-0">
            {(voiceError || chatError) && (
              <p className="text-[10px] text-red-700 bg-red-50 px-2.5 py-1 rounded-lg">
                {voiceError || chatError}
              </p>
            )}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend(null, false);
              }}
              className="flex items-center gap-1.5"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask Genie about meals, cart, prices..."
                disabled={isProcessing}
                className="flex-1 px-3 py-2 rounded-xl bg-[#F2ECFF]/60 border border-[#D8C5FF] text-xs text-[#230852] placeholder:text-[#5B4B7A] focus:outline-none focus:border-[#351078]"
              />
              {isVoiceSupported && (
                <button
                  type="button"
                  onClick={toggleVoice}
                  disabled={isProcessing}
                  className={`p-2 rounded-xl border ${
                    isListening
                      ? 'bg-red-600 text-white border-red-600'
                      : 'bg-[#F2ECFF] text-[#351078] border-[#D8C5FF]'
                  }`}
                  title={isListening ? 'Stop listening' : 'Voice input'}
                >
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>
              )}
              <button
                type="submit"
                disabled={!input.trim() || isProcessing}
                className="p-2 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white disabled:opacity-50"
                title="Send"
              >
                <Send className="w-4 h-4 text-[#C6FF00]" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Fixed Bottom-Right Royal Purple Trigger Button */}
      <button
        type="button"
        onClick={onToggle}
        className="px-4 py-3 rounded-full bg-[#351078] hover:bg-[#4C18AB] text-white shadow-xl border-2 border-[#C6FF00]/70 flex items-center gap-2 transition-transform hover:scale-105"
        aria-label={isOpen ? 'Close Genie Chatbot' : 'Open Genie AI Chatbot'}
      >
        {isOpen ? (
          <X className="w-5 h-5 text-[#C6FF00]" />
        ) : (
          <MessageSquare className="w-5 h-5 text-[#C6FF00]" />
        )}
        <span className="font-display font-bold text-xs sm:text-sm">
          {isOpen ? 'Close Genie' : 'Ask Genie'}
        </span>
      </button>
    </div>
  );
};

export default FloatingGenieChat;

