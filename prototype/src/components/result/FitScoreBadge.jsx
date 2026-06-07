import { useI18n } from '../../i18n';

const VERDICT_KEYS = {
  fits: 'result.fits',
  mostlyFits: 'result.mostlyFits',
  doesntFit: 'result.doesntFit',
};

export default function FitScoreBadge({ score, verdict }) {
  const { t } = useI18n();

  const color =
    verdict === 'fits' ? '#A8B5A2' : verdict === 'mostlyFits' ? '#C9A96E' : '#D4A0A0';

  const circumference = 2 * Math.PI * 54;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="relative w-36 h-36 flex items-center justify-center">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        {/* Background circle */}
        <circle
          cx="60" cy="60" r="54"
          fill="none"
          stroke="#E8E0D4"
          strokeWidth="8"
        />
        {/* Score arc */}
        <circle
          cx="60" cy="60" r="54"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-heading font-bold" style={{ color }}>
          {score}
        </span>
        <span className="text-xs text-espresso/60 mt-0.5">
          {t(VERDICT_KEYS[verdict])}
        </span>
      </div>
    </div>
  );
}
