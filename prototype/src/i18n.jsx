import { createContext, useContext, useState, useCallback } from 'react';
import en from './locales/en.json';
import zh from './locales/zh.json';

const locales = { en, zh };

const I18nContext = createContext();

export function I18nProvider({ children }) {
  const [lang, setLang] = useState(
    () => localStorage.getItem('ai_fit_lang') || 'en'
  );

  const toggleLang = useCallback(() => {
    setLang((prev) => {
      const next = prev === 'en' ? 'zh' : 'en';
      localStorage.setItem('ai_fit_lang', next);
      return next;
    });
  }, []);

  const t = useCallback(
    (key, params = {}) => {
      const keys = key.split('.');
      let val = locales[lang];
      for (const k of keys) {
        val = val?.[k];
      }
      if (typeof val !== 'string') return key;
      return val.replace(/\{(\w+)\}/g, (_, name) =>
        params[name] !== undefined ? params[name] : `{${name}}`
      );
    },
    [lang]
  );

  return (
    <I18nContext.Provider value={{ lang, toggleLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
