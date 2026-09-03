import { getAqiCategory } from '../utils/constants'
import { formatCoordinates } from '../utils/constants'

export default function AQICard({ data, compact = false, location }) {
  const category = getAqiCategory(data?.aqi, data?.category)
  const locationLabel = location?.label || (location?.latitude !== undefined ? `Coordinates ${formatCoordinates(location.latitude, location.longitude)}` : 'Location unavailable')
  return <section className={`card aqi-card ${compact ? 'compact' : ''} tone-${category.tone}`}><div className="card-heading"><div><span className="eyebrow">Current air quality</span><h2>{data?.aqi_display || (data?.aqi ?? 'Data unavailable')}</h2></div><span className="aqi-badge">{category.label}</span></div><div className="aqi-meta"><span>India CPCB scale</span>{data?.dominant_pollutant && <span>Dominant: {data.dominant_pollutant.toUpperCase()}</span>}</div><p className="location-context">Location: {locationLabel}</p>{data?.timestamp && <p className="muted">Updated {new Date(data.timestamp).toLocaleString()}</p>}</section>
}
