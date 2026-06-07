import { useMemo, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useI18n } from '../i18n';
import { useBodyProfile } from '../hooks/useBodyProfile';
import { getProductById } from '../data/products';
import { calculateFit, recommendSize } from '../lib/fitAlgorithm';
import FitScoreBadge from '../components/result/FitScoreBadge';
import FitVisualization from '../components/result/FitVisualization';
import RegionDetail from '../components/result/RegionDetail';
import FitRecommendation from '../components/result/FitRecommendation';
import AlternativeSizes from '../components/result/AlternativeSizes';
import Button from '../components/common/Button';
import Toast from '../components/common/Toast';

const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];

export default function ResultPage() {
  const { productId, size } = useParams();
  const navigate = useNavigate();
  const { t } = useI18n();
  const { profile, hasProfile } = useBodyProfile();
  const [showToast, setShowToast] = useState(false);

  const product = getProductById(productId);

  const fitResult = useMemo(() => {
    if (!hasProfile || !product) return null;
    return calculateFit(profile, product, size);
  }, [hasProfile, profile, product, size]);

  const recommended = useMemo(() => {
    if (!hasProfile || !product) return null;
    return recommendSize(profile, product);
  }, [hasProfile, profile, product]);

  if (!product || !fitResult) {
    return (
      <div className="p-6 text-center">
        <p className="text-espresso/50 mb-4">No fit data available</p>
        <Link to="/catalog" className="text-gold underline text-sm">
          {t('result.backToCatalog')}
        </Link>
      </div>
    );
  }

  const otherSizes = SIZES.filter((s) => s !== size);

  return (
    <div className="px-4 py-6">
      <h2 className="font-heading text-2xl font-bold mb-1">{t('result.title')}</h2>
      <p className="text-sm text-espresso/50 mb-6">
        {product.name} &mdash; {size}
      </p>

      {/* Score gauge */}
      <div className="flex justify-center mb-6">
        <FitScoreBadge score={fitResult.overall} verdict={fitResult.verdict} />
      </div>

      {/* Body visualization */}
      <div className="flex justify-center mb-6">
        <FitVisualization regions={fitResult.regions} gender={profile.gender} />
      </div>

      {/* Region details */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold mb-3">{t('result.regionDetails')}</h3>
        <div className="space-y-3">
          {fitResult.regions.map((region) => (
            <RegionDetail key={region.name} region={region} />
          ))}
        </div>
      </div>

      {/* Recommendation */}
      <FitRecommendation
        fitResult={fitResult}
        size={size}
        recommended={recommended}
        product={product}
      />

      {/* Alternative sizes */}
      <AlternativeSizes
        sizes={otherSizes}
        currentSize={size}
        productId={productId}
        recommended={recommended}
      />

      {/* Actions */}
      <div className="space-y-3 mt-6">
        <Button onClick={() => setShowToast(true)}>
          {t('result.addToCart')}
        </Button>
        <Link
          to="/catalog"
          className="block text-center text-sm text-espresso/50 hover:text-espresso transition-colors"
        >
          {t('result.backToCatalog')}
        </Link>
      </div>

      {showToast && (
        <Toast message={t('result.added')} onClose={() => setShowToast(false)} />
      )}
    </div>
  );
}
