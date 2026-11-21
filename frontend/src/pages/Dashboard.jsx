import { useEffect } from 'react'

import AQICard from '../components/AQICard'
import PollutantCard from '../components/PollutantCard'
import ForecastCard from '../components/ForecastCard'
import MapCard from '../components/MapCard'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import SectionHeader from '../components/SectionHeader'

import { formatCoordinates } from '../utils/constants'
import { useAirQuality } from '../hooks/useAirQuality'
import { usePrediction } from '../hooks/usePrediction'
import { useCurrentLocation } from '../hooks/useCurrentLocation'

export default function Dashboard() {
    // Get the citizen's current device location.
    const {
        location,
        loading: locationLoading,
        error: locationError,
        getLocation
    } = useCurrentLocation()

    // Ask for location permission when the dashboard loads.
    useEffect(() => {
        getLocation()
    }, [getLocation])

    // Pass actual device coordinates to the backend APIs.
    const air = useAirQuality(location)
    const prediction = usePrediction(location)

    const pollutants = Object.entries(air.current?.pollutants || {})

    const locationLabel = location
        ? `Coordinates ${formatCoordinates(location.latitude, location.longitude)}`
        : 'Location unavailable'

    // Show loading while the browser is obtaining the citizen's location.
    if (locationLoading || !location && !locationError) {
        return (
            <div className="page-intro">
                <div>
                    <span className="eyebrow">Current air-quality coordinates</span>
                    <h1>Know the air around you.</h1>
                    <p>Allow location access to view air quality around your current location.</p>
                </div>
                <LoadingState label="Getting your current location..." />
            </div>
        )
    }

    // Show an error if the citizen denies location permission or location is unavailable.
    if (!location) {
        return (
            <>
                <div className="page-intro">
                    <div>
                        <span className="eyebrow">Current air-quality coordinates</span>
                        <h1>Know the air around you.</h1>
                        <p>Location access is required to retrieve air-quality information for your area.</p>
                    </div>
                    <div className="location-pill">◎ Location unavailable</div>
                </div>

                <ErrorState
                    message={locationError || 'Unable to access your current location. Please enable location permission in your browser.'}
                    onRetry={getLocation}
                />
            </>
        )
    }

    return (
        <>
            <div className="page-intro">
                <div>
                    <span className="eyebrow">Current air-quality coordinates</span>
                    <h1>Know the air around you.</h1>
                    <p>Live conditions and model-based outlooks for clearer everyday decisions.</p>
                </div>

                <div className="location-pill">
                    ◎ {locationLabel}
                </div>
            </div>

            {air.loading ? (
                <LoadingState label="Loading current air quality and stations..." />
            ) : air.error ? (
                <ErrorState
                    message={air.error}
                    onRetry={air.retry}
                />
            ) : (
                <>
                    <div className="dashboard-grid">
                        <AQICard
                            data={air.current}
                            location={location}
                        />

                        <div className="card advisory-teaser">
                            <span className="eyebrow">General guidance</span>
                            <h3>{air.current?.category || 'Current conditions'} air quality</h3>
                            <p>
                                Explore your personalized guidance using your health profile
                                and current device location.
                            </p>
                            <a className="text-link" href="/health">
                                Get health guidance →
                            </a>
                        </div>
                    </div>

                    <SectionHeader
                        eyebrow="What is in the air"
                        title="Pollutant concentrations"
                    />

                    <p className="location-context">
                        Same current-air-quality location: {locationLabel}
                    </p>

                    <div className="pollutant-grid">
                        {pollutants.length ? (
                            pollutants.map(([name, pollutant]) => (
                                <PollutantCard
                                    key={name}
                                    name={name}
                                    pollutant={pollutant}
                                />
                            ))
                        ) : (
                            <p className="muted">
                                Pollutant readings are unavailable.
                            </p>
                        )}
                    </div>

                    <div className="two-column">
                        <div>
                            {prediction.loading ? (
                                <LoadingState label="Loading AQI forecast..." />
                            ) : prediction.error ? (
                                <ErrorState
                                    message={prediction.error}
                                    onRetry={prediction.retry}
                                />
                            ) : (
                                <ForecastCard
                                    forecast={prediction.data?.forecast}
                                    location={prediction.data}
                                    modelStation={prediction.data?.historical_station}
                                />
                            )}
                        </div>

                        <div className="card source-card">
                            <span className="eyebrow">Data provenance</span>
                            <h3>Built for informed action</h3>
                            <p>
                                Current readings come from the connected air-quality service.
                                Forecasts use the system's existing prediction model and
                                local weather inputs.
                            </p>
                        </div>
                    </div>

                    <MapCard stations={air.stations} />
                </>
            )}
        </>
    )
}