export const DEFAULT_LOCATION = { latitude: 19.076, longitude: 72.8777 }

export function formatCoordinates(latitude, longitude) {
  const lat = Number(latitude)
  const lon = Number(longitude)
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return 'Location unavailable'
  return `${lat.toFixed(4)}, ${lon.toFixed(4)}`
}

export const CONDITIONS = [
  'Asthma',
  'COPD / Chronic Lung Condition',
  'Other Respiratory Condition',
  'Heart / Cardiovascular Condition',
  'Diabetes',
  'Allergies / Sinusitis',
  'Pregnancy',
  'Other / Not Listed',
]

export const AGE_GROUPS = [
  ['18-30 years', '18-30 years'],
  ['31-50 years', '31-50 years'],
  ['51-65 years', '51-65 years'],
  ['65+ years', '65+ years'],
]

export const ACTIVITY_LEVELS = [
  ['Light Activity', 'Light Activity'],
  ['Moderate Activity', 'Moderate Activity'],
  ['Heavy Exercise', 'Heavy Activity'],
]

export const AQI_CATEGORIES = [
  { max: 50, label: 'Good', tone: 'good' },
  { max: 100, label: 'Satisfactory', tone: 'satisfactory' },
  { max: 200, label: 'Moderate', tone: 'moderate' },
  { max: 300, label: 'Poor', tone: 'poor' },
  { max: 400, label: 'Very Poor', tone: 'very-poor' },
  { max: Infinity, label: 'Severe', tone: 'severe' },
]

export function getAqiCategory(value, fallback) {
  if (fallback) return fallback
  const numeric = Number(value)
  return Number.isFinite(numeric)
    ? AQI_CATEGORIES.find((item) => numeric <= item.max) || AQI_CATEGORIES.at(-1)
    : { label: 'Unavailable', tone: 'unknown' }
}
