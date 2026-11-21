
import { useEffect, useState } from 'react'

import AQICard from '../components/AQICard'
import PollutantCard from '../components/PollutantCard'
import ForecastCard from '../components/ForecastCard'
import MapCard from '../components/MapCard'
import WeatherImpact from '../components/WeatherImpact'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import SectionHeader from '../components/SectionHeader'

import { useAirQuality } from '../hooks/useAirQuality'
import { usePrediction } from '../hooks/usePrediction'
import { useCurrentLocation } from '../hooks/useCurrentLocation'

import { getWeatherForecast } from '../services/advisoryService'
import { formatCoordinates } from '../utils/constants'

export default function AQI() {
    // Get the citizen's actual device location
    const {
        location,
        loading: locationLoading,
        error: locationError,
        getLocation,
    } = useCurrentLocation()

    // Request location when the page loads
    useEffect(() => {
        getLocation()
    }, [getLocation])

    // Use the same device coordinates for all AQI-related APIs
    const air = useAirQuality(location)
    const prediction = usePrediction(location)

    const [weather, setWeather] = useState({
        data: null,
        loading: true,
        error: '',
    })

    // Fetch weather using the citizen's actual coordinates
    useEffect(() => {
        if (
            location?.latitude == null ||
            location?.longitude == null
        ) {
            return
        }

        let cancelled = false

        setWeather({
            data: null,
            loading: true,
            error: '',
        })

        getWeatherForecast(
            location.latitude,
            location.longitude
        )
            .then((data) => {
                if (!cancelled) {
                    setWeather({
                        data,
                        loading: false,
                        error: '',
                    })
                }
            })
            .catch((error) => {
                console.error(error)

                if (!cancelled) {
                    setWeather({
                        data: null,
                        loading: false,
                        error: 'Unable to load weather data.',
                    })
                }
            })

        return () => {
            cancelled = true
        }
    }, [location?.latitude, location?.longitude])

    const locationLabel = location
        ? `Coordinates ${formatCoordinates(
            location.latitude,
            location.longitude
        )}`
        : 'Getting your location...'

    // Handle location permission and retrieval
    if (locationLoading && !location) {
        return <LoadingState label="Getting your current location..." />
    }

    if (locationError && !location) {
        return (
            <>
                <div className="page-intro">
                    <div>
                        <span className="eyebrow">Air quality intelligence</span>
                        <h1>See the full picture.</h1>
                        <p>Allow location access to view air quality and weather around you.</p>
                    </div>
                </div>

                <ErrorState
                    message={locationError}
                    onRetry={getLocation}
                />
            </>
        )
    }

    return (
        <>
            <div className="page-intro">
                <div>
                    <span className="eyebrow">
                        Air quality intelligence
                    </span>

                    <h1>See the full picture.</h1>

                    <p>
                        Compare current readings, forecast movement,
                        and atmospheric context.
                    </p>
                </div>

                <div className="location-pill">
                    ◎ {locationLabel}
                </div>
            </div>

            {air.loading ? (
                <LoadingState label="Loading AQI data..." />
            ) : air.error ? (
                <ErrorState
                    message={air.error}
                    onRetry={air.retry}
                />
            ) : (
                <>
                    <AQICard
                        data={air.current}
                        compact
                        location={location}
                    />

                    <SectionHeader
                        eyebrow="Forward view"
                        title="AQI forecast"
                    />

                    {prediction.loading ? (
                        <LoadingState label="Loading forecast..." />
                    ) : prediction.error ? (
                        <ErrorState
                            message={prediction.error}
                            onRetry={prediction.retry}
                        />
                    ) : (
                        <ForecastCard
                            forecast={prediction.data?.forecast}
                            title="Available forecast periods"
                            location={prediction.data}
                            modelStation={prediction.data?.historical_station}
                        />
                    )}

                    <div className="two-column">
                        <div>
                            {weather.loading ? (
                                <LoadingState label="Loading weather factors..." />
                            ) : weather.error ? (
                                <ErrorState message={weather.error} />
                            ) : (
                                <WeatherImpact
                                    forecast={weather.data?.forecast}
                                    location={weather.data}
                                />
                            )}
                        </div>

                        <div>
                            <SectionHeader
                                eyebrow="Around you"
                                title="Pollutants"
                            />

                            <p className="location-context">
                                Same current-air-quality location: {locationLabel}
                            </p>

                            <div className="pollutant-grid">
                                {Object.entries(
                                    air.current?.pollutants || {}
                                ).map(([name, pollutant]) => (
                                    <PollutantCard
                                        key={name}
                                        name={name}
                                        pollutant={pollutant}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>

                    <MapCard stations={air.stations} />
                </>
            )}
        </>
    )
}
