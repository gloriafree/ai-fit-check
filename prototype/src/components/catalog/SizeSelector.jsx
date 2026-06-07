import { useI18n } from '../../i18n';

export default function SizeSelector({ sizes, selected, recommended, onSelect }) {
  const { t } = useI18n();

  return (
    <div className="flex gap-2">
      {sizes.map((size) => {
        const isSelected = size === selected;
        const isRecommended = size === recommended;

        return (
          <button
            key={size}
            onClick={() => onSelect(size)}
            className={`relative flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
              isSelected
                ? 'bg-espresso text-cream'
                : 'bg-white text-espresso/60 border border-espresso/15 hover:border-espresso/30'
            }`}
          >
            {size}
            {isRecommended && (
              <span className="absolute -top-1.5 left-1/2 -translate-x-1/2 text-[8px] text-gold font-semibold bg-cream px-1 rounded">
                {t('product.recommended')}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
