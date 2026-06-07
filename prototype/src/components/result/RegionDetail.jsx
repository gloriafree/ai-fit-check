import { useI18n } from '../../i18n';

export default function RegionDetail({ region }) {
  const { t } = useI18n();

  const color =
    region.score >= 80 ? '#A8B5A2' : region.score >= 60 ? '#C9A96E' : '#D4A0A0';

  const regionLabel = t(`product.${region.name}`);
  const fitLabel = t(`result.${region.label}`);

  return (
    <div className="bg-white rounded-xl p-3">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm font-medium">{regionLabel}</span>
        <div className="flex items-center gap-2">
          <span className="text-xs text-espresso/50">
            {t('result.ease')}: {region.ease > 0 ? '+' : ''}{region.ease}cm
          </span>
          <span
            className="text-xs font-medium px-2 py-0.5 rounded-full"
            style={{ backgroundColor: color + '30', color }}
          >
            {fitLabel}
          </span>
        </div>
      </div>
      <div className="h-2 bg-espresso/10 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${region.score}%`, backgroundColor: color }}
        />
      </div>
      <div className="text-right mt-0.5">
        <span className="text-xs text-espresso/40">{region.score}/100</span>
      </div>
    </div>
  );
}
