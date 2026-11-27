import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Loader2 } from 'lucide-react';

const SPEECH_LANG_MAP = {
  en: 'en-IN',
  te: 'te-IN',
  hi: 'hi-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
};

export const BottomChatInput = ({
  onSendMessage,
  isProcessing = false,
  activeLanguage = 'en',
  compact = false,
  placeholder = 'Ask Genie anything about healthy food, your cart, or nutrition...',
}) => {
  const [text, setText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  const textareaRef = useRef(null);
  const recognitionRef = useRef(null);

  const SpeechRecognition =
    typeof window !== 'undefined'
      ? window.SpeechRecognition || window.webkitSpeechRecognition
      : null;
  const isVoiceSupported = Boolean(SpeechRecognition);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 100)}px`;
    }
  }, [text]);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
      }
    };
  }, []);

  const handleSend = (viaVoice = false) => {
    const clean = text.trim();
    if (!clean || isProcessing) return;

    setVoiceError(null);
    onSendMessage(clean, viaVoice);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(false);
    }
  };

  const toggleVoiceInput = () => {
    if (!SpeechRecognition || isProcessing) return;
    setVoiceError(null);

    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = SPEECH_LANG_MAP[activeLanguage] || 'en-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript?.trim();
        if (transcript) {
          setText((prev) => (prev ? `${prev} ${transcript}` : transcript));
        }
      };
      recognition.onerror = (event) => {
        setIsListening(false);
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setVoiceError('Microphone permission denied. Please type your message.');
        } else {
          setVoiceError('Voice input unavailable right now. Please type your message.');
        }
      };
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
      recognition.start();
    } catch (_) {
      setIsListening(false);
      setVoiceError('Could not start voice input in this browser.');
    }
  };

  return (
    <div className={compact ? 'w-full' : 'w-full pt-3'}>
      {voiceError && (
        <p className="text-[11px] text-red-700 bg-red-50 border border-red-200 rounded-xl px-3 py-1.5 mb-2">
          {voiceError}
        </p>
      )}

      <div className="flex items-end gap-2 bg-white rounded-2xl border border-[#D8C5FF] shadow-card focus-within:border-[#351078] p-2 transition-colors">
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isProcessing}
          className="flex-1 max-h-28 bg-transparent text-xs sm:text-sm text-[#230852] placeholder:text-[#5B4B7A] resize-none px-2.5 py-2 focus:outline-none leading-relaxed"
        />

        {isVoiceSupported && (
          <button
            type="button"
            onClick={toggleVoiceInput}
            disabled={isProcessing}
            className={`p-2 rounded-xl border transition-colors flex-shrink-0 ${
              isListening
                ? 'bg-red-600 text-white border-red-600'
                : 'bg-[#F2ECFF] hover:bg-[#E5DAFB] text-[#351078] border-[#D8C5FF]'
            }`}
            title={isListening ? 'Stop listening' : 'Voice input'}
            aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
        )}

        <button
          type="button"
          onClick={() => handleSend(false)}
          disabled={!text.trim() || isProcessing}
          className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors flex-shrink-0 ${
            text.trim() && !isProcessing
              ? 'bg-[#351078] hover:bg-[#4C18AB] text-white shadow-xs cursor-pointer'
              : 'bg-[#F2ECFF] text-[#5B4B7A] cursor-not-allowed'
          }`}
          title="Send message"
        >
          {isProcessing ? (
            <Loader2 className="w-4 h-4 animate-spin text-[#C6FF00]" />
          ) : (
            <Send className="w-4 h-4 text-[#C6FF00]" />
          )}
          {!compact && <span>Send</span>}
        </button>
      </div>

      {!compact && (
        <p className="text-[11px] text-center text-[#5B4B7A] mt-2">
          Nutrition guidance is based on ICMR-NIN &amp; USDA reference data. Values and food prices are estimates.
        </p>
      )}
    </div>
  );
};

export default BottomChatInput;
