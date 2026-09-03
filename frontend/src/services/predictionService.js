import { request } from './api'

export const getAQIForecast = (latitude, longitude, forecastDays = 3) =>
  request(`/prediction/forecast?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}&forecast_days=${forecastDays}`)
