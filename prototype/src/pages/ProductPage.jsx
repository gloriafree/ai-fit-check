import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useI18n } from '../i18n';
import { useBodyProfile } from '../hooks/useBodyProfile';
import { getProductById } from '../data/products';
import { getSizeChart } from '../data/sizeCharts';
import { calculateFit, recommendSize } from '../lib/fitAlgorithm';
import SizeSelector from '../components/catalog/SizeSelector';
import Button from '../components/common/Button';

const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];

export default function ProductPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useI18n();
  const { profile, hasProfile } = useBodyProfile();

  const product = getProductById(id);
  const sizeChart = getSizeChart(id);
  const [showChart, setShowChart] = useState(false);

  const recommended = useMemo(() => {
    if (!hasProfile || !product) return null;
    return recommendSize(profile, product);
  }, [hasProfile, profile, product]);

  const [selectedSize, setSelectedSize] = useState(null);

  // Set default to recommended once available
  const activeSize = selectedSize || recommended || 'M';

  const fitPreview = useMemo(() => {
    if (!hasProfile || !product) return null;
    return calculateFit(profile, product, activeSize);
  }, [hasProfile, profile, product, activeSize]);

  if (!product) {
    return <div className="p-6 text-center text-espresso/50">Product not found</div>;
  }

  return (
    <div className="px-4 py-6">
      {/* Product image placeholder */}
      <div className="w-full aspect-[3/4] bg-white rounded-2xl mb-4 flex items-center justify-center overflow-hidden">
        <div className="text-6xl">{product.emoji}</div>
      </div>

      <h2 className="font-heading text-xl font-bold">{product.name}</h2>
      <p className="text-sm text-espresso/50 mb-1">{product.brand}</p>
      <p className="text-lg font-semibold text-gold mb-4">${product.price}</p>

      {/* Size selector */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">{t('product.size')}</span>
          <button
            onClick={() => setShowChart(!showChart)}
            className="text-xs text-gold underline"
          >
            {t('product.sizeChart')}
          </button>
        </div>
        <SizeSelector
          sizes={SIZES}
          selected={activeSize}
          recommended={recommended}
          onSelect={(s) => setSelectedSize(s)}
        />
      </div>

      {/* Size chart table */}
      {showChart && sizeChart && (
        <div className="mb-4 overflow-x-auto bg-white rounded-xl p-3">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-espresso/10">
                <th className="text-left py-1 pr-2">{t('product.size')}</th>
                <th className="text-center py-1 px-2">{t('product.chest')}</th>
                <th className="text-center py-1 px-2">{t('product.shoulder')}</th>
                <th className="text-center py-1 px-2">{t('product.waist')}</th>
                <th className="text-center py-1 px-2">{t('product.length')}</th>
              </tr>
            </thead>
            <tbody>
              {SIZES.map((size) => (
                <tr
                  key={size}
                  className={`border-b border-espresso/5 ${
                    size === activeSize ? 'bg-gold/10 font-semibold' : ''
                  }`}
                >
                  <td className="py-1.5 pr-2">{size}</td>
                  <td className="text-center py-1.5 px-2">{sizeChart[size]?.chest}</td>
                  <td className="text-center py-1.5 px-2">{sizeChart[size]?.shoulder}</td>
                  <td className="text-center py-1.5 px-2">{sizeChart[size]?.waist}</td>
                  <td className="text-center py-1.5 px-2">{sizeChart[size]?.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Fit preview */}
      {fitPreview && (
        <div className="mb-5 p-3 bg-white rounded-xl">
          <p className="text-xs font-medium text-espresso/60 mb-2">{t('product.fitPreview')}</p>
          <div className="space-y-2">
            {fitPreview.regions.map((r) => (
              <div key={r.name} className="flex items-center gap-2">
                <span className="text-xs w-16 shrink-0">{t(`product.${r.name}`)}</span>
                <div className="flex-1 h-2 bg-espresso/10 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${r.score}%`,
                      backgroundColor:
                        r.score >= 80 ? '#A8B5A2' : r.score >= 60 ? '#C9A96E' : '#D4A0A0',
                    }}
                  />
                </div>
                <span className="text-xs w-8 text-right">{r.score}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <Button
        onClick={() => navigate(`/result/${id}/${activeSize}`)}
        disabled={!hasProfile}
      >
        {t('product.checkFit')}
      </Button>

      {!hasProfile && (
        <p className="text-xs text-center text-espresso/40 mt-2">
          {t('catalog.noProfile')}
        </p>
      )}
    </div>
  );
}
