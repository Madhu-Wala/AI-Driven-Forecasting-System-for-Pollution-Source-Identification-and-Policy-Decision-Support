import { useCallback, useEffect, useMemo, useState } from 'react'
import ErrorState from '../../components/ErrorState'
import LoadingState from '../../components/LoadingState'
import MapCard from '../../components/MapCard'
import SourceComparisonChart from '../../components/policy/SourceComparisonChart'
import SourceScoreCard from '../../components/policy/SourceScoreCard'
import StationSelector from '../../components/policy/StationSelector'
import { getSourceAnalysis } from '../../services/policyService'

function displayValue(value, digits = 3) {
  return Number.isFinite(value) ? value.toFixed(digits) : 'Unavailable'
}

export default function SourceAnalysis() {
  const [state, setState] = useState({ stations: [], loading: true, error: '' })
  const [selection, setSelection] = useState({ stationId: '', search: '' })

  const load = useCallback(async () => {
    setState((previous) => ({ ...previous, loading: true, error: '' }))
    try {
      const response = await getSourceAnalysis()
      const stations = Array.isArray(response.stations) ? response.stations : []
      setState({ stations, loading: false, error: '' })
      setSelection((previous) => ({
        ...previous,
        stationId: stations.some((station) => station.station_id === previous.stationId)
          ? previous.stationId
          : stations[0]?.station_id || '',
      }))
    } catch (error) {
      console.error(error)
      setState((previous) => ({ ...previous, loading: false, error: error.message || 'Unable to load source analysis.' }))
    }
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => { load() }, 0)
    return () => clearTimeout(timer)
  }, [load])

  const selected = useMemo(
    () => state.stations.find((station) => station.station_id === selection.stationId) || null,
    [state.stations, selection.stationId],
  )
  const scores = selected?.source_scores || selected?.category_scores || {}
  const anomalies = selected?.pollutant_anomalies || {}
  const currentPollutants = selected?.current_pollutants || {}
  const pollutantRows = [
    ['NO₂ anomaly', anomalies.no2],
    ['CO anomaly', anomalies.co],
    ['PM10 anomaly', anomalies.pm10],
    ['Coarse PM anomaly', anomalies.coarse_pm],
    ['SO₂ anomaly', anomalies.so2],
  ]
  const selectStation = (station) => setSelection((previous) => ({ ...previous, stationId: station.station_id }))

  return <>
    <div className="page-intro">
      <div><span className="eyebrow">Policy Maker · Station signals</span><h1>Source Analysis</h1><p>Analyse pollutant patterns associated with Transport, Road Dust and Industry across Mumbai monitoring stations.</p></div>
      {selected?.timestamp && <div className="location-pill">Observation {new Date(selected.timestamp).toLocaleString()}</div>}
    </div>

    {state.loading && <LoadingState label="Loading station source signals…" />}
    {state.error && <ErrorState message={state.error} onRetry={load} />}
    {!state.loading && !state.error && !state.stations.length && <div className="card empty-result"><h3>No station source data available</h3><p className="muted">The API returned no station records. Check database availability and try again.</p></div>}

    {selected && <>
      <section className="card policy-station-toolbar">
        <StationSelector stations={state.stations} value={selection} onChange={setSelection} />
        <div><span className="eyebrow">Selected station</span><strong>{selected.station_name || selected.station_id}</strong><span className="muted">{selected.station_id} · {selected.latitude ?? '—'}, {selected.longitude ?? '—'}</span></div>
      </section>

      <SourceScoreCard scores={scores} labels={selected.source_signal_labels || {}} />

      <div className="two-column policy-analysis-grid">
        <section className="card">
          <div className="section-heading"><div><span className="eyebrow">Selected station</span><h3>Station-wise source comparison</h3></div></div>
          <SourceComparisonChart scores={scores} />
        </section>
        <section className="card">
          <div className="section-heading"><div><span className="eyebrow">Observed deviations</span><h3>Pollutant anomaly details</h3></div></div>
          <div className="policy-data-list">
            {pollutantRows.map(([label, anomaly]) => {
              const pollutant = label.startsWith('NO₂') ? 'no2'
                : label.startsWith('CO ') ? 'co'
                  : label.startsWith('PM10') ? 'pm10'
                    : label.startsWith('Coarse') ? 'coarse_pm' : 'so2'
              return <div className="policy-data-row" key={label}>
                <span>{label}</span>
                <strong>{displayValue(anomaly)}</strong>
                <small>Current: {displayValue(currentPollutants[pollutant], 2)}</small>
              </div>
            })}
          </div>
        </section>
      </div>

      <section className="card policy-reliability">
        <div className="section-heading"><div><span className="eyebrow">Measurement completeness</span><h3>Data reliability</h3></div><strong className="coverage-value">{selected.data_coverage?.coverage_percentage ?? 'Unavailable'}{selected.data_coverage?.coverage_percentage != null ? '%' : ''}</strong></div>
        <div className="coverage-summary">
          <span>Available indicators: <strong>{selected.data_coverage?.available_indicators ?? 'Unavailable'}</strong></span>
          <span>Total indicators: <strong>{selected.data_coverage?.total_indicators ?? 'Unavailable'}</strong></span>
        </div>
        <h4>Baseline sample counts</h4>
        {selected.baseline_sample_counts && Object.keys(selected.baseline_sample_counts).length
          ? <div className="baseline-grid">{Object.entries(selected.baseline_sample_counts).map(([name, count]) => <span key={name}>{name.replaceAll('_', ' ')} <strong>{count}</strong></span>)}</div>
          : <p className="muted">Baseline sample counts are unavailable.</p>}
        <h4>Unavailable indicators</h4>
        {selected.data_coverage?.unavailable_indicators?.length
          ? <p>{selected.data_coverage.unavailable_indicators.join(', ')}</p>
          : <p className="muted">No unavailable indicators were reported.</p>}
      </section>

      <div className="policy-map-section">
        <h2 className="policy-section-title">Select a station on the map</h2>
        <MapCard stations={state.stations} onStationSelect={selectStation} selectedStationId={selected.station_id} />
        <p className="muted">Selecting a marker updates the station selector and source anomaly details above.</p>
      </div>

      <aside className="policy-interpretation">
        <strong>How to interpret these scores</strong>
        <p>Source anomaly scores represent signed normalized pollutant deviations from historical baselines. Positive values indicate above-baseline pollutant signals, while negative values indicate below-baseline signals. These are heuristic indicators and do not represent actual emission contribution percentages or confirmed pollution sources.</p>
        {selected.interpretation && <p className="muted">{selected.interpretation}</p>}
      </aside>
    </>}
  </>
}
