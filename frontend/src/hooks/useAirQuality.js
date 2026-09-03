import { useCallback, useEffect, useState } from 'react'
import { getCurrentAirQuality, getStations } from '../services/airQualityService'
import { DEFAULT_LOCATION } from '../utils/constants'

export function useAirQuality(location = DEFAULT_LOCATION) {
  const [state, setState] = useState({ current: null, stations: [], loading: true, error: '' })

  const load = useCallback(async () => {
    setState((previous) => ({ ...previous, loading: true, error: '' }))
    try {
      const [current, stationResponse] = await Promise.all([
        getCurrentAirQuality(location.latitude, location.longitude),
        getStations(),
      ])
      setState({ current, stations: stationResponse.stations || [], loading: false, error: '' })
    } catch (error) {
      console.error(error)
      setState((previous) => ({ ...previous, loading: false, error: 'Unable to load air-quality data.' }))
    }
  }, [location.latitude, location.longitude])

  useEffect(() => {
    const timer = setTimeout(() => { load() }, 0)
    return () => clearTimeout(timer)
  }, [load])
  return { ...state, retry: load }
}
