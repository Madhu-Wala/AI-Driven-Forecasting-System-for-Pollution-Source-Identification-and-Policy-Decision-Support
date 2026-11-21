
import { useCallback, useState } from 'react'

export function useCurrentLocation() {
  const [location, setLocation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const getLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Your browser does not support location access.')
      return
    }

    setLoading(true)
    setError('')

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        })
        setLoading(false)
      },
      (err) => {
        let message = 'Unable to determine your current location.'

        if (err.code === 1) {
          message = 'Location permission denied. Please allow location access.'
        } else if (err.code === 2) {
          message = 'Your current location is unavailable. Please try again.'
        } else if (err.code === 3) {
          message = 'Location request timed out. Please try again.'
        }

        setError(message)
        setLoading(false)
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 60000,
      }
    )
  }, [])

  return { location, loading, error, getLocation }
}