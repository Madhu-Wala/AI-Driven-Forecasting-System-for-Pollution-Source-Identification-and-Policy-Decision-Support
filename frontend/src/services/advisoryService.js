import { request } from './api'

export const generateAdvisory = (payload) =>
  request('/api/advisory/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const getWeatherForecast = (latitude, longitude, forecastDays = 2) =>
  request(`/weather/forecast?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}&forecast_days=${forecastDays}`)
