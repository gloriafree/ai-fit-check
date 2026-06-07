// Recommended ease values (cm) per fit type
export const EASE_BY_FIT_TYPE = {
  slim: {
    chest: 4,
    shoulder: 1,
    waist: 3,
    hip: 3,
  },
  regular: {
    chest: 8,
    shoulder: 2,
    waist: 6,
    hip: 5,
  },
  oversized: {
    chest: 16,
    shoulder: 4,
    waist: 12,
    hip: 10,
  },
};

// Tolerance bands per region (cm) — how much deviation from ideal ease is acceptable
// Lower tolerance = more sensitive (shoulder most sensitive, waist most forgiving)
export const TOLERANCE = {
  shoulder: 1.5,
  chest: 3,
  waist: 4,
  hip: 3.5,
};

// Scoring weights per region
export const REGION_WEIGHTS = {
  chest: 0.35,
  shoulder: 0.30,
  waist: 0.20,
  hip: 0.15,
};

// Input ranges for measurement sliders
export const MEASUREMENT_RANGES = {
  height: { min: 140, max: 200, step: 1, unit: 'cm' },
  weight: { min: 35, max: 130, step: 0.5, unit: 'kg' },
  chest: { min: 70, max: 130, step: 0.5, unit: 'cm' },
  waist: { min: 55, max: 110, step: 0.5, unit: 'cm' },
  hip: { min: 70, max: 130, step: 0.5, unit: 'cm' },
  shoulder: { min: 30, max: 55, step: 0.5, unit: 'cm' },
  armLength: { min: 45, max: 75, step: 0.5, unit: 'cm' },
};

// Default body profile
export const DEFAULT_PROFILE = {
  gender: 'female',
  height: 165,
  weight: 58,
  chest: 88,
  waist: 68,
  hip: 94,
  shoulder: null,
  armLength: null,
};
