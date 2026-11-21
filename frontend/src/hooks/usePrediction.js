
import { useCallback, useEffect, useState } from 'react'
import { getAQIForecast } from '../services/predictionService'

export function usePrediction(location) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: '',
  })

  const latitude = location?.latitude
  const longitude = location?.longitude

  const load = useCallback(async () => {
    // Wait until the citizen's location is available
    if (latitude == null || longitude == null) {
      return
    }

    setState((previous) => ({
      ...previous,
      loading: true,
      error: '',
    }))

    try {
      const data = await getAQIForecast(latitude, longitude)

      setState({
        data,
        loading: false,
        error: '',
      })
    } catch (error) {
      console.error(error)

      setState({
        data: null,
        loading: false,
        error: 'Unable to load AQI forecast.',
      })
    }
  }, [latitude, longitude])

  useEffect(() => {
    if (latitude == null || longitude == null) {
      return
    }

    const timer = setTimeout(() => {
      load()
    }, 0)

    return () => clearTimeout(timer)
  }, [load, latitude, longitude])

  return {
    ...state,
    retry: load,
  }
}
