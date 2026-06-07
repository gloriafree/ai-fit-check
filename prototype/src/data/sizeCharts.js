// Garment measurements in cm — sourced from real brand standard grading
// Each entry: { chest, shoulder, waist, hip, length }

const sizeCharts = {
  'classic-tee': {
    XS: { chest: 86, shoulder: 39, waist: 82, hip: 86, length: 63 },
    S:  { chest: 92, shoulder: 41, waist: 88, hip: 92, length: 65 },
    M:  { chest: 96, shoulder: 43, waist: 92, hip: 96, length: 67 },
    L:  { chest: 102, shoulder: 45, waist: 98, hip: 102, length: 69 },
    XL: { chest: 108, shoulder: 47, waist: 104, hip: 108, length: 71 },
    XXL:{ chest: 114, shoulder: 49, waist: 110, hip: 114, length: 73 },
  },

  'slim-oxford': {
    XS: { chest: 84, shoulder: 38, waist: 76, hip: 84, length: 68 },
    S:  { chest: 88, shoulder: 40, waist: 80, hip: 88, length: 70 },
    M:  { chest: 92, shoulder: 42, waist: 84, hip: 92, length: 72 },
    L:  { chest: 96, shoulder: 44, waist: 88, hip: 96, length: 74 },
    XL: { chest: 100, shoulder: 46, waist: 92, hip: 100, length: 76 },
    XXL:{ chest: 104, shoulder: 48, waist: 96, hip: 104, length: 78 },
  },

  'oversized-hoodie': {
    XS: { chest: 100, shoulder: 44, waist: 96, hip: 100, length: 66 },
    S:  { chest: 106, shoulder: 46, waist: 102, hip: 106, length: 68 },
    M:  { chest: 112, shoulder: 48, waist: 108, hip: 112, length: 70 },
    L:  { chest: 118, shoulder: 50, waist: 114, hip: 118, length: 72 },
    XL: { chest: 124, shoulder: 52, waist: 120, hip: 124, length: 74 },
    XXL:{ chest: 130, shoulder: 54, waist: 126, hip: 130, length: 76 },
  },

  'fitted-polo': {
    XS: { chest: 84, shoulder: 38, waist: 78, hip: 84, length: 64 },
    S:  { chest: 88, shoulder: 40, waist: 82, hip: 88, length: 66 },
    M:  { chest: 92, shoulder: 42, waist: 86, hip: 92, length: 68 },
    L:  { chest: 96, shoulder: 44, waist: 90, hip: 96, length: 70 },
    XL: { chest: 100, shoulder: 46, waist: 94, hip: 100, length: 72 },
    XXL:{ chest: 104, shoulder: 48, waist: 98, hip: 104, length: 74 },
  },

  'relaxed-tank': {
    XS: { chest: 82, shoulder: 34, waist: 80, hip: 84, length: 60 },
    S:  { chest: 88, shoulder: 36, waist: 86, hip: 90, length: 62 },
    M:  { chest: 94, shoulder: 38, waist: 92, hip: 96, length: 64 },
    L:  { chest: 100, shoulder: 40, waist: 98, hip: 102, length: 66 },
    XL: { chest: 106, shoulder: 42, waist: 104, hip: 108, length: 68 },
    XXL:{ chest: 112, shoulder: 44, waist: 110, hip: 114, length: 70 },
  },

  'quilted-vest': {
    XS: { chest: 90, shoulder: 40, waist: 86, hip: 90, length: 58 },
    S:  { chest: 96, shoulder: 42, waist: 92, hip: 96, length: 60 },
    M:  { chest: 102, shoulder: 44, waist: 98, hip: 102, length: 62 },
    L:  { chest: 108, shoulder: 46, waist: 104, hip: 108, length: 64 },
    XL: { chest: 114, shoulder: 48, waist: 110, hip: 114, length: 66 },
    XXL:{ chest: 120, shoulder: 50, waist: 116, hip: 120, length: 68 },
  },

  'linen-shirt': {
    XS: { chest: 88, shoulder: 40, waist: 84, hip: 88, length: 67 },
    S:  { chest: 94, shoulder: 42, waist: 90, hip: 94, length: 69 },
    M:  { chest: 100, shoulder: 44, waist: 96, hip: 100, length: 71 },
    L:  { chest: 106, shoulder: 46, waist: 102, hip: 106, length: 73 },
    XL: { chest: 112, shoulder: 48, waist: 108, hip: 112, length: 75 },
    XXL:{ chest: 118, shoulder: 50, waist: 114, hip: 118, length: 77 },
  },

  'oversized-tee': {
    XS: { chest: 98, shoulder: 44, waist: 94, hip: 98, length: 68 },
    S:  { chest: 104, shoulder: 46, waist: 100, hip: 104, length: 70 },
    M:  { chest: 110, shoulder: 48, waist: 106, hip: 110, length: 72 },
    L:  { chest: 116, shoulder: 50, waist: 112, hip: 116, length: 74 },
    XL: { chest: 122, shoulder: 52, waist: 118, hip: 122, length: 76 },
    XXL:{ chest: 128, shoulder: 54, waist: 124, hip: 128, length: 78 },
  },
};

export function getSizeChart(productId) {
  return sizeCharts[productId] || null;
}
