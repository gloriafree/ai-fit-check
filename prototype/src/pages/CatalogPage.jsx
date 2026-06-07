import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useI18n } from '../i18n';
import { useBodyProfile } from '../hooks/useBodyProfile';
import { products } from '../data/products';
import { getQuickFit } from '../lib/fitAlgorithm';
import ProductGrid from '../components/catalog/ProductGrid';
import Badge from '../components/common/Badge';

const SUBCATEGORIES = ['all', 't-shirt', 'shirt', 'hoodie', 'polo', 'tank', 'vest'];
const FIT_TYPES = ['all', 'slim', 'regular', 'oversized'];

export default function CatalogPage() {
  const { t } = useI18n();
  const { profile, hasProfile } = useBodyProfile();
  const [subcat, setSubcat] = useState('all');
  const [fitType, setFitType] = useState('all');

  const filtered = useMemo(() => {
    return products.filter((p) => {
      if (subcat !== 'all' && p.subcategory !== subcat) return false;
      if (fitType !== 'all' && p.fitType !== fitType) return false;
      return true;
    });
  }, [subcat, fitType]);

  const productsWithFit = useMemo(() => {
    if (!hasProfile) return filtered.map((p) => ({ ...p, quickFit: null }));
    return filtered.map((p) => ({
      ...p,
      quickFit: getQuickFit(profile, p),
    }));
  }, [filtered, hasProfile, profile]);

  return (
    <div className="px-4 py-6">
      <h2 className="font-heading text-2xl font-bold mb-4">{t('catalog.title')}</h2>

      {!hasProfile && (
        <Link
          to="/profile"
          className="block mb-4 p-3 bg-gold/10 rounded-xl text-center text-sm"
        >
          <p className="text-espresso/70">{t('catalog.noProfile')}</p>
          <span className="text-gold font-semibold mt-1 inline-block">
            {t('catalog.setupProfile')} &rarr;
          </span>
        </Link>
      )}

      {/* Subcategory chips */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-3 scrollbar-hide">
        {SUBCATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setSubcat(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
              subcat === cat
                ? 'bg-espresso text-cream'
                : 'bg-white text-espresso/70 border border-espresso/15'
            }`}
          >
            {cat === 'all' ? t('catalog.all') : cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {/* Fit type chips */}
      <div className="flex gap-2 mb-5">
        {FIT_TYPES.map((ft) => (
          <button
            key={ft}
            onClick={() => setFitType(ft)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
              fitType === ft
                ? 'bg-gold text-white'
                : 'bg-white text-espresso/70 border border-espresso/15'
            }`}
          >
            {ft === 'all' ? t('catalog.all') : t(`catalog.${ft}`)}
          </button>
        ))}
      </div>

      <ProductGrid products={productsWithFit} />
    </div>
  );
}
