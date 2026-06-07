import { useI18n } from '../../i18n';

export default function FitRecommendation({ fitResult, size, recommended, product }) {
  const { t } = useI18n();

  let text;
  const regionLabel = t(`product.${fitResult.worstRegion.name}`);

  if (fitResult.verdict === 'fits') {
    text = t('result.recFits', { size, region: regionLabel });
  } else if (fitResult.verdict === 'mostlyFits') {
    const suggestion =
      fitResult.worstRegion.label === 'tooTight' || fitResult.worstRegion.label === 'slightlyTight'
        ? 'sizing up'
        : 'sizing down';
    text = t('result.recMostly', { size, suggestion, region: regionLabel });
  } else {
    text = t('result.recDoesntFit', { size, altSize: recommended });
  }

  return (
    <div className="mb-4 p-4 bg-white rounded-xl border border-espresso/10">
      <h3 className="text-sm font-semibold mb-2">{t('result.recommendation')}</h3>
      <p className="text-sm text-espresso/70 leading-relaxed">{text}</p>
    </div>
  );
}
