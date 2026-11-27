import React, { createContext, useContext, useState, useEffect } from 'react';
import { LANGUAGES, translations } from './translations';

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    try {
      const saved = localStorage.getItem('foodgenie_lang');
      if (saved && translations[saved]) {
        return saved;
      }
      // Auto-detect browser language if supported
      const navLang = navigator.language?.split('-')[0];
      if (navLang && translations[navLang]) {
        return navLang;
      }
    } catch (e) {
      console.warn('Storage or navigator access error:', e);
    }
    return 'en';
  });

  const setLanguage = (langCode) => {
    if (translations[langCode]) {
      setLanguageState(langCode);
      try {
        localStorage.setItem('foodgenie_lang', langCode);
      } catch (e) {
        console.error('Failed to save language preference:', e);
      }
    }
  };

  const t = translations[language] || translations.en;

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, LANGUAGES }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

