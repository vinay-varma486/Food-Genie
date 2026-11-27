import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, CheckCircle, Volume2, VolumeX, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { FoodCardDetailed } from './FoodCardDetailed';
import { FoodRestrictionCard } from './FoodRestrictionCard';

const TTS_LANG_MAP = {
  en: 'en-IN',
  te: 'te-IN',
  hi: 'hi-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
};

function escapeHtml(raw) {
  return String(raw)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function formatInlineMarkdown(text) {
  const safe = escapeHtml(text);
  return safe
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-[#230852]">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
}

export function GenieFormattedResponse({ content }) {
  const str = typeof content === 'string' ? content : (content?.text || (content ? String(content) : ''));
  if (!str || !str.trim()) return null;

  const lines = str.split('\n');
  const elements = [];
  let tableLines = [];
  let inTable = false;

  const flushTable = (key) => {
    if (tableLines.length === 0) return;
    const headerLine = tableLines[0] || '';
    const dataLines = tableLines.slice(2);
    const headers = headerLine.split('|').map((c) => c.trim()).filter(Boolean);
    const rows = dataLines.map((line) => line.split('|').map((c) => c.trim()).filter(Boolean));

    elements.push(
      <div key={`table-${key}`} className="my-3 overflow-x-auto rounded-xl border border-[#D8C5FF] bg-white">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="bg-[#351078] text-white uppercase tracking-wider font-bold">
              {headers.map((h, hi) => (
                <th key={hi} className="py-2.5 px-3 whitespace-nowrap">{h.replace(/\*\*/g, '')}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F2ECFF]">
            {rows.map((row, ri) => (
              <tr key={ri} className="hover:bg-[#FAF7FF] transition-colors">
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    className={`py-2 px-3 whitespace-nowrap ${
                      ci === 0 ? 'font-bold text-[#351078]' : 'text-[#230852] font-medium'
                    }`}
                  >
                    {String(cell).replace(/\*\*/g, '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
    tableLines = [];
    inTable = false;
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      inTable = true;
      tableLines.push(trimmed);
    } else {
      if (inTable) flushTable(index);

      if (trimmed.startsWith('#### ')) {
        const title = trimmed.replace(/^####\s+/, '').replace(/\*\*/g, '');
        elements.push(
          <h4 key={index} className="text-sm font-extrabold text-[#351078] mt-3 mb-1">
            {title}
          </h4>
        );
      } else if (trimmed.startsWith('### ')) {
        const title = trimmed.replace(/^###\s+/, '').replace(/\*\*/g, '');
        elements.push(
          <h3 key={index} className="text-sm font-extrabold text-[#351078] mt-4 mb-1.5 pb-1 border-b border-[#E5DAFB]">
            {title}
          </h3>
        );
      } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        const bulletText = trimmed.replace(/^[-*]\s+/, '');
        elements.push(
          <p key={index} className="text-xs sm:text-sm text-[#230852] leading-relaxed my-1 pl-3 border-l-2 border-[#351078]/35">
            <span dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(bulletText) }} />
          </p>
        );
      } else if (trimmed.length > 0) {
        elements.push(
          <p key={index} className="text-sm text-[#230852] leading-relaxed my-1.5">
            <span dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(trimmed) }} />
          </p>
        );
      }
    }
  });

  if (inTable) flushTable('last');
  return <div className="space-y-1">{elements}</div>;
}

export const MainChatArea = ({
  messages = [],
  isProcessing = false,
  onAskGenie,
  onAddToCart,
  onLogFood,
  cartFoodIds = new Set(),
}) => {
  const messagesEndRef = useRef(null);
  const [speakingMsgId, setSpeakingMsgId] = useState(null);
  const [expandedCards, setExpandedCards] = useState({});

  const isTtsSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  useEffect(() => {
    if (messages.length > 0 || isProcessing) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [messages.length, isProcessing]);

  useEffect(() => {
    return () => {
      if (isTtsSupported) {
        try {
          window.speechSynthesis.cancel();
        } catch (_) {}
      }
    };
  }, [isTtsSupported]);

  const handleToggleSpeak = (msg) => {
    if (!isTtsSupported) return;
    if (speakingMsgId === msg.id) {
      window.speechSynthesis.cancel();
      setSpeakingMsgId(null);
      return;
    }
    window.speechSynthesis.cancel();
    const cleanSpeech = (msg.text || '')
      .replace(/\|[^\n]+\|/g, ' ')
      .replace(/[#*_`]/g, '')
      .slice(0, 750);
    const utterance = new SpeechSynthesisUtterance(cleanSpeech);
    utterance.lang = TTS_LANG_MAP[msg.language] || 'en-IN';
    utterance.onend = () => setSpeakingMsgId(null);
    utterance.onerror = () => setSpeakingMsgId(null);
    setSpeakingMsgId(msg.id);
    window.speechSynthesis.speak(utterance);
  };

  if (messages.length === 0 && !isProcessing) {
    return null;
  }

  return (
    <div className="space-y-4 py-3 max-h-[58vh] overflow-y-auto pr-1">
      {messages.map((msg) => {
        const isUser = msg.sender === 'user';
        const recs = msg.recommendations || [];
        const showAll = Boolean(expandedCards[msg.id]);
        const visibleRecs = showAll ? recs : recs.slice(0, 4);

        return (
          <div
            key={msg.id}
            className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[94%] sm:max-w-[86%] rounded-2xl p-4 shadow-xs ${
                isUser
                  ? 'bg-[#351078] text-white rounded-br-sm'
                  : msg.isError
                  ? 'bg-red-50 border border-red-200 text-red-800 rounded-bl-sm'
                  : 'bg-[#FAF7FF] border border-[#D8C5FF] text-[#230852] rounded-bl-sm'
              }`}
            >
              {!isUser && !msg.isError && (
                <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-[#E5DAFB] gap-2">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-lg bg-[#351078] text-[#C6FF00] flex items-center justify-center">
                      <Sparkles className="w-3.5 h-3.5" />
                    </div>
                    <span className="font-bold text-xs text-[#351078]">Genie AI</span>
                    {msg.language && (
                      <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-[#EEF8FC] border border-[#ADD8E6] text-[#230852]">
                        {msg.language}
                      </span>
                    )}
                  </div>

                  {isTtsSupported && msg.text && (
                    <button
                      type="button"
                      onClick={() => handleToggleSpeak(msg)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white hover:bg-[#F2ECFF] border border-[#D8C5FF] text-[11px] font-bold text-[#351078] transition-colors"
                      title={speakingMsgId === msg.id ? 'Stop speaking' : 'Listen to response'}
                    >
                      {speakingMsgId === msg.id ? (
                        <>
                          <VolumeX className="w-3 h-3 text-red-600" />
                          <span>Stop</span>
                        </>
                      ) : (
                        <>
                          <Volume2 className="w-3 h-3 text-[#351078]" />
                          <span>Listen</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              )}

              {isUser ? (
                <p className="text-sm whitespace-pre-wrap leading-relaxed font-medium">{msg.text}</p>
              ) : (
                <GenieFormattedResponse content={msg.text} />
              )}

              {/* Verified Nutritional Cards with Add to My Food Cart */}
              {recs.length > 0 && (
                <div className="mt-4 pt-3 border-t border-[#D8C5FF] space-y-3">
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <p className="text-[11px] font-extrabold uppercase tracking-wider text-[#351078] flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-[#16A34A]" />
                      <span>Recommended Foods ({recs.length})</span>
                    </p>
                    {recs.length > 4 && (
                      <button
                        type="button"
                        onClick={() => setExpandedCards((p) => ({ ...p, [msg.id]: !p[msg.id] }))}
                        className="inline-flex items-center gap-1 text-xs font-bold text-[#351078] hover:underline"
                      >
                        <span>{showAll ? 'Show less' : `Show all ${recs.length}`}</span>
                        {showAll ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {visibleRecs.map((item, idx) => (
                      <FoodCardDetailed
                        key={item.id || idx}
                        food={item}
                        language={msg.language || 'en'}
                        isInCart={cartFoodIds.has(item.id)}
                        onAddToCart={onAddToCart}
                        onLogFood={onLogFood}
                        onAskGenie={onAskGenie}
                      />
                    ))}
                  </div>
                </div>
              )}

              {msg.restrictions && msg.restrictions.length > 0 && (
                <div className="mt-3 pt-3 border-t border-[#D8C5FF] space-y-2">
                  <p className="text-[11px] font-extrabold uppercase tracking-wider text-rose-700">
                    Foods to Limit or Avoid
                  </p>
                  {msg.restrictions.map((res, idx) => (
                    <FoodRestrictionCard key={idx} restriction={res} />
                  ))}
                </div>
              )}
            </div>

            {msg.timestamp && (
              <span className="text-[10px] text-[#5B4B7A] mt-1 px-1">{msg.timestamp}</span>
            )}
          </div>
        );
      })}

      {isProcessing && (
        <div className="flex items-center gap-2.5 px-4 py-3 rounded-xl bg-[#EEF8FC] border border-[#ADD8E6] w-fit text-xs font-bold text-[#351078]">
          <Loader2 className="w-4 h-4 animate-spin text-[#351078]" />
          <span>Genie is thinking...</span>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MainChatArea;
