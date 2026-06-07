import { useNavigate } from 'react-router-dom';
import { useI18n } from '../../i18n';

export default function AlternativeSizes({ sizes, currentSize, productId, recommended }) {
  const navigate = useNavigate();
  const { t } = useI18n();

  return (
    <div className="mb-2">
      <h3 className="text-sm font-semibold mb-2">{t('result.alternativeSizes')}</h3>
      <div className="flex gap-2 flex-wrap">
        {sizes.map((size) => (
          <button
            key={size}
            onClick={() => navigate(`/result/${productId}/${size}`)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              size === recommended
                ? 'bg-gold text-white'
                : 'bg-white text-espresso/60 border border-espresso/15 hover:border-espresso/30'
            }`}
          >
            {size}
            {size === recommended && (
              <span className="ml-1 text-xs">*</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
