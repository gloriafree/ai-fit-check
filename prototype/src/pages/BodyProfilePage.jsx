import { useState, useCallback } from 'react';
import { useI18n } from '../i18n';
import { useBodyProfile } from '../hooks/useBodyProfile';
import MeasurementForm from '../components/body/MeasurementForm';
import BodySilhouette from '../components/body/BodySilhouette';
import Toast from '../components/common/Toast';

export default function BodyProfilePage() {
  const { t } = useI18n();
  const { profile, updateProfile } = useBodyProfile();
  const [activeRegion, setActiveRegion] = useState(null);
  const [showToast, setShowToast] = useState(false);

  const handleSave = useCallback(() => {
    setShowToast(true);
  }, []);

  return (
    <div className="px-4 py-6">
      <h2 className="font-heading text-2xl font-bold mb-1">{t('profile.title')}</h2>
      <p className="text-xs text-espresso/50 mb-6">{t('profile.subtitle')}</p>

      <div className="flex justify-center mb-6">
        <BodySilhouette activeRegion={activeRegion} gender={profile.gender} />
      </div>

      <MeasurementForm
        profile={profile}
        onChange={updateProfile}
        onFocus={setActiveRegion}
        onSave={handleSave}
      />

      {showToast && (
        <Toast message={t('profile.saved')} onClose={() => setShowToast(false)} />
      )}
    </div>
  );
}
