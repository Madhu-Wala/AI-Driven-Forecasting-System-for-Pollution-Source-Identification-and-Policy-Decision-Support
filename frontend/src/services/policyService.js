import { request } from './api'

export const getPolicyCurrentAirQuality = (latitude, longitude) =>
  request(`/api/air-quality/current?lat=${encodeURIComponent(latitude)}&lon=${encodeURIComponent(longitude)}`)

export const getPolicyStations = () => request('/api/pollution/current')

export const getPolicyForecast = (latitude, longitude, forecastDays = 3) =>
  request(`/prediction/forecast?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}&forecast_days=${forecastDays}`)

export const getPolicyWeather = (latitude, longitude, forecastDays = 2) =>
  request(`/weather/forecast?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}&forecast_days=${forecastDays}`)

export const getSourceAnalysis = () => request('/api/source-identification/')

export const getStationAnalytics = (stationId) =>
  request(`/api/analytics/history/${encodeURIComponent(stationId)}`)
