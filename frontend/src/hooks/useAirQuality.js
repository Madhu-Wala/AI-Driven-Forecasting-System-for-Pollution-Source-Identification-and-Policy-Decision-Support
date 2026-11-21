
import { useCallback, useEffect, useState } from 'react'
import { getCurrentAirQuality, getStations } from '../services/airQualityService'

export function useAirQuality(location) {
  const [state, setState] = useState({
    current: null,
    stations: [],
    loading: true,
    error: '',
  })

  const load = useCallback(async () => {
    if (!location) return

    setState((previous) => ({
      ...previous,
      loading: true,
      error: '',
    }))

    try {
      const [current, stationResponse] = await Promise.all([
        getCurrentAirQuality(location.latitude, location.longitude),
        getStations(),
      ])

      setState({
        current,
        stations: stationResponse.stations || [],
        loading: false,
        error: '',
      })
    } catch (error) {
      console.error(error)

      setState((previous) => ({
        ...previous,
        loading: false,
        error: 'Unable to load air-quality data.',
      }))
    }
  }, [location?.latitude, location?.longitude])

  useEffect(() => {
    if (location) {
      load()
    }
  }, [location, load])

  return { ...state, retry: load }
}