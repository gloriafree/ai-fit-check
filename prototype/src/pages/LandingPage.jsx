import { Link } from 'react-router-dom';
import { useI18n } from '../i18n';

export default function LandingPage() {
  const { t } = useI18n();

  return (
    <div className="px-6 py-8">
      <div className="text-center mb-10">
        <h2 className="font-heading text-3xl font-bold mb-3">{t('landing.title')}</h2>
        <p className="text-espresso/60 text-sm">{t('landing.subtitle')}</p>
      </div>

      <div className="space-y-4 mb-10">
        {[
          { num: '1', title: t('landing.step1'), desc: t('landing.step1Desc') },
          { num: '2', title: t('landing.step2'), desc: t('landing.step2Desc') },
          { num: '3', title: t('landing.step3'), desc: t('landing.step3Desc') },
        ].map((step) => (
          <div key={step.num} className="flex items-start gap-4 p-4 bg-white rounded-xl shadow-sm">
            <div className="w-8 h-8 rounded-full bg-gold/20 text-gold flex items-center justify-center font-semibold text-sm shrink-0">
              {step.num}
            </div>
            <div>
              <h3 className="font-semibold text-sm">{step.title}</h3>
              <p className="text-xs text-espresso/50 mt-0.5">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>

      <Link
        to="/profile"
        className="block w-full text-center py-3 bg-espresso text-cream rounded-xl font-semibold text-sm hover:bg-espresso/90 transition-colors"
      >
        {t('landing.cta')}
      </Link>
    </div>
  );
}
