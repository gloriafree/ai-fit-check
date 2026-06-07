import { EASE_BY_FIT_TYPE, TOLERANCE, REGION_WEIGHTS } from '../constants/measurements';
import { getSizeChart } from '../data/sizeCharts';

const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];

/**
 * Calculate region score based on ease vs ideal ease.
 * Score 100 = perfect ease match, decreasing as deviation grows.
 */
function regionScore(bodyMeasurement, garmentMeasurement, idealEase, tolerance) {
  if (!bodyMeasurement || !garmentMeasurement) return null;

  const actualEase = garmentMeasurement - bodyMeasurement;
  const deviation = Math.abs(actualEase - idealEase);

  // Score decreases linearly from 100, with tolerance defining the "acceptable" band
  // Beyond 2x tolerance, score floors at 0
  const maxDeviation = tolerance * 2.5;
  const score = Math.max(0, Math.round(100 * (1 - deviation / maxDeviation)));

  // Determine fit label
  let label;
  if (actualEase < idealEase - tolerance) {
    label = actualEase < idealEase - tolerance * 2 ? 'tooTight' : 'slightlyTight';
  } else if (actualEase > idealEase + tolerance) {
    label = actualEase > idealEase + tolerance * 2 ? 'tooLoose' : 'slightlyLoose';
  } else {
    label = 'ideal';
  }

  return { score, label, ease: actualEase, idealEase };
}

/**
 * Calculate full fit result for a product + size combination.
 */
export function calculateFit(profile, product, size) {
  const chart = getSizeChart(product.id);
  if (!chart || !chart[size]) return null;

  const garment = chart[size];
  const idealEase = EASE_BY_FIT_TYPE[product.fitType];

  const regions = [];

  // Chest
  const chestResult = regionScore(profile.chest, garment.chest, idealEase.chest, TOLERANCE.chest);
  if (chestResult) regions.push({ name: 'chest', weight: REGION_WEIGHTS.chest, ...chestResult });

  // Shoulder (use estimated if not provided)
  const shoulderBody = profile.shoulder || estimateShoulder(profile);
  const shoulderResult = regionScore(shoulderBody, garment.shoulder, idealEase.shoulder, TOLERANCE.shoulder);
  if (shoulderResult) regions.push({ name: 'shoulder', weight: REGION_WEIGHTS.shoulder, ...shoulderResult });

  // Waist
  const waistResult = regionScore(profile.waist, garment.waist, idealEase.waist, TOLERANCE.waist);
  if (waistResult) regions.push({ name: 'waist', weight: REGION_WEIGHTS.waist, ...waistResult });

  // Hip
  const hipResult = regionScore(profile.hip, garment.hip, idealEase.hip, TOLERANCE.hip);
  if (hipResult) regions.push({ name: 'hip', weight: REGION_WEIGHTS.hip, ...hipResult });

  // Weighted overall score
  const totalWeight = regions.reduce((sum, r) => sum + r.weight, 0);
  const overall = Math.round(
    regions.reduce((sum, r) => sum + r.score * r.weight, 0) / totalWeight
  );

  // Verdict
  let verdict;
  if (overall >= 80) verdict = 'fits';
  else if (overall >= 60) verdict = 'mostlyFits';
  else verdict = 'doesntFit';

  // Find worst region for recommendation
  const worstRegion = regions.reduce((worst, r) =>
    r.score < worst.score ? r : worst
  , regions[0]);

  return { overall, verdict, regions, worstRegion, size };
}

/**
 * Estimate shoulder width from chest if not provided.
 * Rough heuristic: shoulder ~ chest * 0.46 for female, 0.48 for male
 */
function estimateShoulder(profile) {
  const factor = profile.gender === 'male' ? 0.48 : 0.46;
  return Math.round(profile.chest * factor * 10) / 10;
}

/**
 * Recommend the best size for a given profile + product.
 */
export function recommendSize(profile, product) {
  const chart = getSizeChart(product.id);
  if (!chart) return 'M';

  let bestSize = 'M';
  let bestScore = -1;

  for (const size of SIZES) {
    const result = calculateFit(profile, product, size);
    if (result && result.overall > bestScore) {
      bestScore = result.overall;
      bestSize = size;
    }
  }

  return bestSize;
}

/**
 * Quick fit indicator for catalog cards.
 * Returns 'green' | 'yellow' | 'red' based on best-size fit.
 */
export function getQuickFit(profile, product) {
  const bestSize = recommendSize(profile, product);
  const result = calculateFit(profile, product, bestSize);
  if (!result) return null;

  if (result.overall >= 80) return 'green';
  if (result.overall >= 60) return 'yellow';
  return 'red';
}
