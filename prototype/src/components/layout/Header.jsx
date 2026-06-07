import { useI18n } from '../../i18n';

export default function Header() {
  const { lang, toggleLang } = useI18n();

  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-espresso/10">
      <h1 className="font-heading text-xl font-bold tracking-wide">AI Fit</h1>
      <button
        onClick={toggleLang}
        className="text-sm px-2 py-1 rounded border border-espresso/20 hover:bg-espresso/5 transition-colors"
      >
        {lang === 'en' ? '中文' : 'EN'}
      </button>
    </header>
  );
}
