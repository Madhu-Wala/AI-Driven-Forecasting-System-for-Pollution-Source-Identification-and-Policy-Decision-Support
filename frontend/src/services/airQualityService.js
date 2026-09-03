import { request } from './api'

export const getCurrentAirQuality = (latitude, longitude) =>
  request(`/api/air-quality/current?lat=${encodeURIComponent(latitude)}&lon=${encodeURIComponent(longitude)}`)

export const getStations = () => request('/api/pollution/current')
