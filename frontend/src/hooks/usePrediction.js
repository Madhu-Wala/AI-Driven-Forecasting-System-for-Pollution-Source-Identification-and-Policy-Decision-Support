import { useCallback, useEffect, useState } from 'react'
import { getAQIForecast } from '../services/predictionService'

export function usePrediction(location) {
  const [state, setState] = useState({ data: null, loading: true, error: '' })
  const load = useCallback(async () => {
    setState((previous) => ({ ...previous, loading: true, error: '' }))
    try {
      const data = await getAQIForecast(location.latitude, location.longitude)
      setState({ data, loading: false, error: '' })
    } catch (error) {
      console.error(error)
      setState({ data: null, loading: false, error: 'Unable to load AQI forecast.' })
    }
  }, [location.latitude, location.longitude])
  useEffect(() => {
    const timer = setTimeout(() => { load() }, 0)
    return () => clearTimeout(timer)
  }, [load])
  return { ...state, retry: load }
}
