import { useCallback, useEffect, useState } from 'react'
import AQICard from '../../components/AQICard'
import ErrorState from '../../components/ErrorState'
import ForecastCard from '../../components/ForecastCard'
import LoadingState from '../../components/LoadingState'
import MapCard from '../../components/MapCard'
import PolicyMetricCard from '../../components/policy/PolicyMetricCard'
import WeatherImpact from '../../components/WeatherImpact'
import { getPolicyCurrentAirQuality, getPolicyForecast, getPolicyStations, getPolicyWeather } from '../../services/policyService'
import { DEFAULT_LOCATION } from '../../utils/constants'

const initialSection = { data: null, error: '', loading: true }

function sectionResult(result) {
  return result.status === 'fulfilled'
    ? { data: result.value, error: '', loading: false }
    : { data: null, error: result.reason?.message || 'Unable to load this data.', loading: false }
}

export default function PolicyOverview() {
  const [air, setAir] = useState(initialSection)
  const [stations, setStations] = useState(initialSection)
  const [forecast, setForecast] = useState(initialSection)
  const [weather, setWeather] = useState(initialSection)

  const load = useCallback(async () => {
    setAir((state) => ({ ...state, loading: true, error: '' }))
    setStations((state) => ({ ...state, loading: true, error: '' }))
    setForecast((state) => ({ ...state, loading: true, error: '' }))
    setWeather((state) => ({ ...state, loading: true, error: '' }))
    const results = await Promise.allSettled([
      getPolicyCurrentAirQuality(DEFAULT_LOCATION.latitude, DEFAULT_LOCATION.longitude),
      getPolicyStations(),
      getPolicyForecast(DEFAULT_LOCATION.latitude, DEFAULT_LOCATION.longitude),
      getPolicyWeather(DEFAULT_LOCATION.latitude, DEFAULT_LOCATION.longitude),
    ])
    setAir(sectionResult(results[0]))
    setStations(sectionResult(results[1]))
    setForecast(sectionResult(results[2]))
    setWeather(sectionResult(results[3]))
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => { load() }, 0)
    return () => clearTimeout(timer)
  }, [load])

  const stationRecords = stations.data?.stations || []
  const updatedAt = air.data?.timestamp
    ? new Date(air.data.timestamp).toLocaleString()
    : null

  return <>
    <div className="page-intro">
      <div><span className="eyebrow">Policy Maker · Overview</span><h1>Policy Overview</h1><p>Monitor Mumbai's air quality and environmental conditions.</p></div>
      {updatedAt && <div className="location-pill">AQI updated {updatedAt}</div>}
    </div>

    <div className="policy-metric-grid">
      <PolicyMetricCard label="Current AQI" value={air.loading ? 'Loading…' : air.data?.aqi ?? 'Unavailable'} detail={air.data?.aqi_scale || 'Coordinate-based provider reading'} tone="blue" />
      <PolicyMetricCard label="AQI category" value={air.loading ? 'Loading…' : air.data?.category || 'Unavailable'} detail={air.data?.dominant_pollutant ? `Dominant pollutant: ${air.data.dominant_pollutant.toUpperCase()}` : 'Dominant pollutant not provided'} tone="green" />
      <PolicyMetricCard label="Monitoring stations" value={stations.loading ? 'Loading…' : stations.data?.count ?? stationRecords.length} detail="Stations with records returned by the API" tone="blue" />
      <PolicyMetricCard label="Forecast periods" value={forecast.loading ? 'Loading…' : forecast.data?.forecast?.length ?? 'Unavailable'} detail="Daily AQI model predictions" tone="amber" />
    </div>

    {air.error && <ErrorState message={`Current AQI: ${air.error}`} onRetry={load} />}
    {stations.error && <ErrorState message={`Station records: ${stations.error}`} onRetry={load} />}
    {forecast.error && <ErrorState message={`AQI forecast: ${forecast.error}`} onRetry={load} />}
    {weather.error && <ErrorState message={`Weather forecast: ${weather.error}`} onRetry={load} />}

    <div className="two-column policy-overview-grid">
      <section>
        <h2 className="policy-section-title">Current air quality</h2>
        {air.loading ? <LoadingState label="Loading current air quality…" /> : air.data ? <AQICard data={air.data} location={DEFAULT_LOCATION} /> : <p className="muted">Current AQI is unavailable.</p>}
      </section>
      <section>
        <h2 className="policy-section-title">AQI forecast</h2>
        {forecast.loading ? <LoadingState label="Loading forecast…" /> : forecast.data ? <ForecastCard forecast={forecast.data.forecast || []} title="Available forecast periods" location={forecast.data} modelStation={forecast.data.historical_station} /> : <p className="muted">Forecast is unavailable.</p>}
      </section>
    </div>

    <div className="two-column policy-overview-grid">
      <section>
        <h2 className="policy-section-title">Monitoring stations</h2>
        {stations.loading ? <LoadingState label="Loading station records…" /> : <MapCard stations={stationRecords} />}
      </section>
      <section>
        <h2 className="policy-section-title">Atmospheric context</h2>
        {weather.loading ? <LoadingState label="Loading weather forecast…" /> : weather.data ? <WeatherImpact forecast={weather.data.forecast || []} location={weather.data} /> : <p className="muted">Weather information is unavailable.</p>}
      </section>
    </div>
  </>
}
