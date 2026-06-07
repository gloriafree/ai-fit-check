import { useI18n } from '../../i18n';
import { MEASUREMENT_RANGES } from '../../constants/measurements';
import MeasurementSlider from './MeasurementSlider';
import Button from '../common/Button';

const REQUIRED_FIELDS = ['height', 'weight', 'chest', 'waist', 'hip'];
const OPTIONAL_FIELDS = ['shoulder', 'armLength'];

// Map field names to region names for silhouette highlighting
const REGION_MAP = {
  chest: 'chest',
  waist: 'waist',
  hip: 'hip',
  shoulder: 'shoulder',
  armLength: 'arm',
  height: null,
  weight: null,
};

export default function MeasurementForm({ profile, onChange, onFocus, onSave }) {
  const { t } = useI18n();

  const handleFieldChange = (field) => (value) => {
    onChange({ [field]: value });
  };

  const handleFieldFocus = (field) => () => {
    onFocus(REGION_MAP[field] || null);
  };

  return (
    <div>
      {/* Gender toggle */}
      <div className="mb-5">
        <label className="text-sm font-medium block mb-2">{t('profile.gender')}</label>
        <div className="flex gap-2">
          {['female', 'male'].map((g) => (
            <button
              key={g}
              onClick={() => onChange({ gender: g })}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                profile.gender === g
                  ? 'bg-espresso text-cream'
                  : 'bg-white text-espresso/60 border border-espresso/15'
              }`}
            >
              {t(`profile.${g}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Required measurements */}
      <div className="mb-2">
        <span className="text-xs text-espresso/40 uppercase tracking-wider">
          {t('profile.required')}
        </span>
      </div>
      {REQUIRED_FIELDS.map((field) => {
        const range = MEASUREMENT_RANGES[field];
        return (
          <MeasurementSlider
            key={field}
            label={t(`profile.${field}`)}
            value={profile[field] || range.min}
            onChange={handleFieldChange(field)}
            onFocus={handleFieldFocus(field)}
            min={range.min}
            max={range.max}
            step={range.step}
            unit={range.unit === 'cm' ? t('profile.cm') : t('profile.kg')}
          />
        );
      })}

      {/* Optional measurements */}
      <div className="mb-2 mt-6">
        <span className="text-xs text-espresso/40 uppercase tracking-wider">
          {t('profile.optional')}
        </span>
      </div>
      {OPTIONAL_FIELDS.map((field) => {
        const range = MEASUREMENT_RANGES[field];
        return (
          <MeasurementSlider
            key={field}
            label={t(`profile.${field}`)}
            value={profile[field] || range.min}
            onChange={handleFieldChange(field)}
            onFocus={handleFieldFocus(field)}
            min={range.min}
            max={range.max}
            step={range.step}
            unit={t('profile.cm')}
          />
        );
      })}

      <div className="mt-6">
        <Button onClick={onSave}>{t('profile.save')}</Button>
      </div>
    </div>
  );
}
