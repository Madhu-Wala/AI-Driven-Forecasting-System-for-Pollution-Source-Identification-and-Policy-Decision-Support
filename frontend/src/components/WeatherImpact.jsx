const labels = { temperature_2m_mean: 'Temperature', relative_humidity_2m_mean: 'Humidity', pressure_msl_mean: 'Pressure', wind_speed_10m_mean: 'Wind speed', precipitation_sum: 'Precipitation' }
import { formatCoordinates } from '../utils/constants'
export default function WeatherImpact({ 
    forecast = [], location }) { 
        const record = forecast[0] || {}; 
        const entries = Object.entries(labels).filter(([key]) => record[key] !== undefined && record[key] !== null); 
        const locationLabel = location ? formatCoordinates(location.latitude, location.longitude) : 'Location unavailable'; 
        return <section className="card weather-impact-card">
            <div className="section-heading">
                <div><span className="eyebrow">Atmospheric context</span>
            <h3>Weather impact</h3><p className="location-context">Weather location: Coordinates {locationLabel}</p></div></div>{entries.length ? <div className="weather-grid">{entries.map(([key, label]) => <div className="weather-row" key={key}><span>{label}</span><strong>{record[key]}</strong></div>)}</div> : <p className="muted">Weather factors are unavailable.</p>}</section> }
