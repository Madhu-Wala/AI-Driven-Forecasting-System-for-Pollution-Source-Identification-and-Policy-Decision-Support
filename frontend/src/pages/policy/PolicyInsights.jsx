import { useCallback, useEffect, useMemo, useState } from 'react'
import ErrorState from '../../components/ErrorState'
import LoadingState from '../../components/LoadingState'
import SourceScoreCard from '../../components/policy/SourceScoreCard'
import StationSelector from '../../components/policy/StationSelector'
import {
  generatePolicyRecommendations,
  getPolicyRagStatus,
  getPolicyStationEvidence,
  getPolicyStations,
  searchPolicyEvidence,
} from '../../services/policyService'

const defaultSelection = { stationId: '', search: '' }

function EvidenceText({ text, expanded, onToggle }) {
  const content = displayValue(text, 'No evidence excerpt available')
  const showToggle = content.length > 260

  return <>
    <p className={`policy-evidence-text ${expanded ? 'expanded' : ''}`}>{content}</p>
    {showToggle && <button className="evidence-toggle" type="button" onClick={onToggle}>{expanded ? 'Show less' : 'Read more'}</button>}
  </>
}

function displayValue(value, fallback = 'Unavailable') {
  if (value === null || value === undefined || value === '') {
    return fallback
  }

  if (typeof value === 'number' && Number.isNaN(value)) {
    return fallback
  }

  return String(value)
}

function formatTimestamp(value) {
  if (!value) {
    return 'Unavailable'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return displayValue(value)
  }

  return date.toLocaleString()
}

function mapAssessmentToScores(sourceAssessment = []) {
  return sourceAssessment.reduce((accumulator, item) => {
    const source = String(item?.source || '').trim()

    if (!source) {
      return accumulator
    }

    accumulator[source.toLowerCase()] = item.score ?? null
    return accumulator
  }, {})
}

function mapAssessmentToSignals(sourceAssessment = []) {
  return sourceAssessment.reduce((accumulator, item) => {
    const source = String(item?.source || '').trim()

    if (!source) {
      return accumulator
    }

    accumulator[source.toLowerCase()] = item.signal || 'unknown'
    return accumulator
  }, {})
}

function getPriorityClass(priority = 'low') {
  switch (priority?.toLowerCase()) {
    case 'high':
      return 'priority-high'
    case 'medium':
      return 'priority-medium'
    default:
      return 'priority-low'
  }
}

function getPriorityText(priority = 'low') {
  switch (priority?.toLowerCase()) {
    case 'high':
      return 'High priority'
    case 'medium':
      return 'Medium priority'
    default:
      return 'Low priority'
  }
}

export default function PolicyInsights() {
  const [ragStatus, setRagStatus] = useState({
    loading: true,
    available: false,
    message: 'Checking policy RAG availability…',
  })

  const [stationState, setStationState] = useState({
    stations: [],
    loading: true,
    error: '',
  })

  const [selection, setSelection] = useState(defaultSelection)
  const [stationEvidence, setStationEvidence] = useState({ data: null, loading: false, error: '' })
  const [recommendations, setRecommendations] = useState({ data: null, loading: false, error: '' })
  const [searchState, setSearchState] = useState({ query: '', data: null, loading: false, error: '' })
  const [expandedEvidence, setExpandedEvidence] = useState({})

  const loadStations = useCallback(async () => {
    setStationState((previous) => ({ ...previous, loading: true, error: '' }))

    try {
      const response = await getPolicyStations()
      const stations = Array.isArray(response?.stations) ? response.stations : []

      setStationState({ stations, loading: false, error: '' })
      setSelection((current) => {
        const stationId = current.stationId && stations.some((station) => String(station.station_id) === String(current.stationId))
          ? current.stationId
          : stations[0]?.station_id || ''

        return { ...current, stationId }
      })
    } catch (error) {
      setStationState({ stations: [], loading: false, error: error.message || 'Unable to load monitoring stations.' })
    }
  }, [])

  useEffect(() => {
    let isMounted = true

    const loadInitialData = async () => {
      try {
        const statusResponse = await getPolicyRagStatus()
        if (!isMounted) {
          return
        }

        setRagStatus({
          loading: false,
          available: Boolean(statusResponse.available),
          message: statusResponse.message || 'Policy RAG status unavailable.',
        })
      } catch (error) {
        if (!isMounted) {
          return
        }

        setRagStatus({
          loading: false,
          available: false,
          message: error.message || 'Policy RAG status check failed.',
        })
      }

      try {
        const response = await getPolicyStations()
        if (!isMounted) {
          return
        }

        const stations = Array.isArray(response?.stations) ? response.stations : []

        setStationState({ stations, loading: false, error: '' })
        setSelection((current) => {
          const nextStationId = current.stationId && stations.some((station) => String(station.station_id) === String(current.stationId))
            ? current.stationId
            : stations[0]?.station_id || ''

          return { ...current, stationId: nextStationId }
        })
      } catch (error) {
        if (!isMounted) {
          return
        }

        setStationState({ stations: [], loading: false, error: error.message || 'Unable to load monitoring stations.' })
      }
    }

    loadInitialData()

    return () => {
      isMounted = false
    }
  }, [])

  const selectedStation = useMemo(
    () => stationState.stations.find((station) => String(station.station_id) === String(selection.stationId)) || null,
    [selection.stationId, stationState.stations],
  )

  const loadStationEvidence = useCallback(async (stationId) => {
    if (!stationId) {
      return
    }

    setStationEvidence({ data: null, loading: true, error: '' })
    setRecommendations({ data: null, loading: false, error: '' })

    try {
      const response = await getPolicyStationEvidence(stationId, 5)
      setStationEvidence({ data: response, loading: false, error: '' })
    } catch (error) {
      setStationEvidence({ data: null, loading: false, error: error.message || 'Unable to load station policy evidence.' })
    }
  }, [])

  useEffect(() => {
    if (!selection.stationId) {
      return
    }

    let isMounted = true

    const fetchStationEvidence = async () => {
      setStationEvidence({ data: null, loading: true, error: '' })
      setRecommendations({ data: null, loading: false, error: '' })

      try {
        const response = await getPolicyStationEvidence(selection.stationId, 5)
        if (!isMounted) {
          return
        }

        setStationEvidence({ data: response, loading: false, error: '' })
      } catch (error) {
        if (!isMounted) {
          return
        }

        setStationEvidence({ data: null, loading: false, error: error.message || 'Unable to load station policy evidence.' })
      }
    }

    fetchStationEvidence()

    return () => {
      isMounted = false
    }
  }, [selection.stationId])

  const sourceAssessment = useMemo(() => {
    const recommendationAssessment = recommendations.data?.policy_response?.source_assessment

    if (Array.isArray(recommendationAssessment) && recommendationAssessment.length) {
      return recommendationAssessment
    }

    const stationData = stationEvidence.data?.station_data || {}
    const categoryScores = stationData.category_scores || {}

    return Object.entries(categoryScores).map(([source, score]) => ({
      source,
      score,
      signal: Number(score) > 0 ? 'positive' : Number(score) < 0 ? 'negative' : Number(score) === 0 ? 'neutral' : 'unknown',
      interpretation: 'Source score is derived from historical pollutant baselines.',
    }))
  }, [recommendations.data, stationEvidence.data])

  const sourceScores = useMemo(() => {
    if (Array.isArray(recommendations.data?.policy_response?.source_assessment)) {
      return mapAssessmentToScores(recommendations.data.policy_response.source_assessment)
    }

    if (stationEvidence.data?.station_data?.category_scores) {
      return stationEvidence.data.station_data.category_scores
    }

    return {}
  }, [recommendations.data, stationEvidence.data])

  const sourceSignals = useMemo(() => {
    if (Array.isArray(recommendations.data?.policy_response?.source_assessment)) {
      return mapAssessmentToSignals(recommendations.data.policy_response.source_assessment)
    }

    if (stationEvidence.data?.station_data?.source_signal_labels) {
      return stationEvidence.data.station_data.source_signal_labels
    }

    return {}
  }, [recommendations.data, stationEvidence.data])

  const evidenceCards = useMemo(() => {
    const evidence = [
      ...(stationEvidence.data?.evidence || []),
      ...(recommendations.data?.policy_response?.evidence || []),
    ]

    const unique = new Map()

    evidence.forEach((item, index) => {
      const id = item?.evidence_id || item?.source || item?.file_name || item?.category || `evidence-${index}`
      if (!unique.has(id)) {
        unique.set(id, item)
      }
    })

    return Array.from(unique.values())
  }, [recommendations.data, stationEvidence.data])

  const policyRecommendations = recommendations.data?.policy_response?.recommendations || []
  const limitations = recommendations.data?.policy_response?.limitations || [
    'Recommendations are evidence-informed suggestions, not guaranteed outcomes.',
    'Source scores are heuristic indicators, not confirmed emission contribution percentages.',
    'Quantitative intervention impact estimates may not be available for every recommendation.',
    'Some responsible authorities may require verification before action is taken.',
  ]

  const stationPollutants = stationEvidence.data?.station_data?.current_pollutants || {}
  const pollutantCards = [
    { label: 'PM2.5', value: stationPollutants.pm25 },
    { label: 'PM10', value: stationPollutants.pm10 },
    { label: 'NO₂', value: stationPollutants.no2 },
    { label: 'SO₂', value: stationPollutants.so2 },
    { label: 'CO', value: stationPollutants.co },
    { label: 'O₃', value: stationPollutants.o3 },
    { label: 'Coarse PM', value: stationPollutants.coarse_pm },
  ]

  const stationSummary = stationEvidence.data?.station_data || selectedStation || {}

  const handleGenerateRecommendations = useCallback(async () => {
    if (!selection.stationId) {
      setRecommendations((current) => ({
        ...current,
        error: 'Select a station before generating policy recommendations.',
      }))
      return
    }

    setRecommendations({ data: null, loading: true, error: '' })

    try {
      const response = await generatePolicyRecommendations(selection.stationId, 5)
      setRecommendations({ data: response, loading: false, error: '' })
    } catch (error) {
      setRecommendations({ data: null, loading: false, error: error.message || 'Unable to generate policy recommendations.' })
    }
  }, [selection.stationId])

  const handleSearchSubmit = useCallback(async (event) => {
    event.preventDefault()

    const query = searchState.query.trim()

    if (!query) {
      setSearchState((current) => ({ ...current, error: 'Enter a policy question or policy topic to search.' }))
      return
    }

    setSearchState({ query, data: null, loading: true, error: '' })

    try {
      const response = await searchPolicyEvidence(query, 5)
      setSearchState({ query, data: response, loading: false, error: '' })
    } catch (error) {
      setSearchState({ query, data: null, loading: false, error: error.message || 'Unable to search policy documents.' })
    }
  }, [searchState.query])

  const searchResults = searchState.data?.evidence || []

  const toggleEvidenceExpansion = useCallback((key) => {
    setExpandedEvidence((current) => ({
      ...current,
      [key]: !current[key],
    }))
  }, [])

  return <>
    <div className="page-intro">
      <div>
        <span className="eyebrow">Policy Maker · Evidence workspace</span>
        <h1>Policy Insights</h1>
        <p>Evidence-based recommendations for urban air-quality management.</p>
      </div>
      <span className={`policy-status ${ragStatus.loading ? 'status-checking' : ragStatus.available ? 'status-available' : 'status-unavailable'}`}>
        {ragStatus.loading ? 'Checking' : ragStatus.available ? 'Available' : 'Unavailable'}
      </span>
    </div>

    {ragStatus.message && !ragStatus.loading && !ragStatus.available && (
      <ErrorState message={ragStatus.message} />
    )}

    <section className="card">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Station selection</span>
          <h2>Current assessment</h2>
        </div>
      </div>

      <div className="policy-insights-station-toolbar">
        <StationSelector stations={stationState.stations} value={selection} onChange={setSelection} label="Monitoring station" />

        <div className="station-detail-panel">
          <div className="station-detail-card">
            <span className="eyebrow">Selected station</span>
            <strong>{selectedStation?.station_name || stationSummary.station_name || 'No station selected'}</strong>
            <span>{selectedStation?.station_id || stationSummary.station_id || 'Unavailable'}{selectedStation?.station_id ? ` • ${selectedStation.station_id}` : ''}</span>
          </div>
          <div className="station-facts-grid">
            <div className="station-detail-card compact">
              <span className="eyebrow">AQI</span>
              <strong>{displayValue(stationSummary.aqi || selectedStation?.aqi, 'Unavailable')}</strong>
            </div>
            <div className="station-detail-card compact">
              <span className="eyebrow">AQI category</span>
              <strong>{displayValue(stationSummary.aqi_category || selectedStation?.aqi_category, 'Unavailable')}</strong>
            </div>
            <div className="station-detail-card compact">
              <span className="eyebrow">Latest timestamp</span>
              <strong>{formatTimestamp(stationSummary.timestamp || selectedStation?.timestamp)}</strong>
            </div>
          </div>
        </div>
      </div>

      {stationState.loading && <LoadingState label="Loading station data…" />}
      {stationState.error && <ErrorState message={stationState.error} onRetry={loadStations} />}

      {!stationState.loading && !selectedStation && !stationState.error && (
        <div className="card empty-result">
          <h3>No stations are currently available.</h3>
          <p className="muted">The station dataset is empty or the backend is unavailable.</p>
        </div>
      )}

      {!stationState.loading && selectedStation && (
        <div className="policy-pollutant-grid">
          {pollutantCards.map((pollutant) => (
            <div className="policy-pollutant-card" key={pollutant.label}>
              <span>{pollutant.label}</span>
              <strong>{Number.isFinite(Number(pollutant.value)) ? Number(pollutant.value).toFixed(2) : 'Unavailable'}</strong>
            </div>
          ))}
        </div>
      )}

      {stationEvidence.loading && <LoadingState label="Loading station policy evidence…" />}
      {stationEvidence.error && <ErrorState message={stationEvidence.error} onRetry={() => loadStationEvidence(selection.stationId)} />}
    </section>

    <div className="page-section-heading">
      <div>
        <span className="eyebrow">Source signal assessment</span>
        <h2>Sector source scores</h2>
      </div>
    </div>

    {sourceAssessment.length > 0 ? (
      <SourceScoreCard scores={sourceScores} labels={sourceSignals} />
    ) : (
      <div className="card empty-result">
        <h3>No source signal data is available.</h3>
        <p className="muted">The selected station has not returned source-assessment values yet.</p>
      </div>
    )}

    <p className="source-signal-note">
      Source scores are heuristic indicators of pollutant deviations from historical baselines. They do not represent confirmed emission contribution percentages.
    </p>

    <div className="page-section-heading">
      <div>
        <span className="eyebrow">AI-generated recommendations</span>
        <h2>Policy recommendations</h2>
      </div>
      <button className="button button-primary" onClick={handleGenerateRecommendations} disabled={recommendations.loading || !selection.stationId} type="button">
        {recommendations.loading ? 'Generating…' : 'Generate Policy Recommendations'}
      </button>
    </div>

    {recommendations.error && <ErrorState message={recommendations.error} onRetry={handleGenerateRecommendations} />}

    {!recommendations.loading && !recommendations.error && policyRecommendations.length === 0 && (
      <div className="card empty-result">
        <h3>No recommendations were generated.</h3>
        <p className="muted">The selected station does not currently have enough supported evidence to create a defensible policy recommendation.</p>
      </div>
    )}

    {recommendations.loading && <LoadingState label="Generating station recommendations…" />}

    <div className="recommendation-list">
      {policyRecommendations.map((recommendation, index) => {
        const evidenceIds = Array.isArray(recommendation.evidence_ids) ? recommendation.evidence_ids : []
        const responsibleAuthority = displayValue(recommendation.responsible_authority, 'Relevant authority to be verified')
        const expectedImpact = recommendation.expected_impact || {}
        const quantitativeStatus = expectedImpact.quantitative_estimate_available === false
          ? 'Validated quantitative estimate unavailable'
          : displayValue(expectedImpact.quantitative_estimate, 'Validated quantitative estimate unavailable')

        return <details className="card recommendation-card" key={`${recommendation.recommendation_id || 'recommendation'}-${index}`} open={index === 0}>
          <summary>
            <div className="recommendation-summary-main">
              <div className="recommendation-summary-header">
                <span className="recommendation-title">{displayValue(recommendation.title, 'Untitled recommendation')}</span>
                <span className={`priority-pill ${getPriorityClass(recommendation.priority)}`}>{getPriorityText(recommendation.priority)}</span>
              </div>
              <small>{displayValue(recommendation.recommendation_id, 'No recommendation ID')} • {responsibleAuthority}</small>
            </div>
          </summary>
          <div className="recommendation-body">
            <div className="recommendation-meta-grid">
              <div>
                <span className="eyebrow">Priority</span>
                <p>{getPriorityText(recommendation.priority)}</p>
              </div>
              <div>
                <span className="eyebrow">Recommendation ID</span>
                <p>{displayValue(recommendation.recommendation_id, 'Unavailable')}</p>
              </div>
              <div>
                <span className="eyebrow">Responsible authority</span>
                <p>{responsibleAuthority}</p>
              </div>
            </div>

            <div className="recommendation-meta-grid">
              <div>
                <span className="eyebrow">Intervention</span>
                <p>{displayValue(recommendation.intervention, 'No intervention provided')}</p>
              </div>
              <div>
                <span className="eyebrow">Rationale</span>
                <p>{displayValue(recommendation.rationale, 'No rationale provided')}</p>
              </div>
            </div>

            <div className="recommendation-meta-grid">
              <div>
                <span className="eyebrow">Implementation conditions</span>
                {Array.isArray(recommendation.implementation_conditions) && recommendation.implementation_conditions.length
                  ? <ul className="recommendation-list-items">{recommendation.implementation_conditions.map((condition, conditionIndex) => <li key={`${recommendation.recommendation_id}-condition-${conditionIndex}`}>{displayValue(condition, 'Condition unavailable')}</li>)}</ul>
                  : <p>Implementation conditions are not specified.</p>}
              </div>
              <div>
                <span className="eyebrow">Expected impact</span>
                <p>{displayValue(expectedImpact.description, 'No expected impact description available')}</p>
                <p className="muted">{quantitativeStatus}</p>
              </div>
            </div>

            <div>
              <span className="eyebrow">Evidence IDs</span>
              <div className="recommendation-evidence">
                {evidenceIds.length
                  ? evidenceIds.map((id) => <span className="evidence-tag" key={`${recommendation.recommendation_id}-${id}`}>{id}</span>)
                  : <span className="muted">No evidence IDs were provided for this recommendation.</span>}
              </div>
            </div>
          </div>
        </details>
      })}
    </div>

    <div className="page-section-heading">
      <div>
        <span className="eyebrow">Government evidence</span>
        <h2>Supporting government evidence</h2>
      </div>
    </div>

    {evidenceCards.length ? (
      <div className="policy-evidence-grid">
        {evidenceCards.map((item, index) => {
          const evidenceId = item?.evidence_id || `Evidence ${index + 1}`
          const category = displayValue(item?.category, 'Unknown category')
          const source = displayValue(item?.source, 'Source path unavailable')
          const excerpt = displayValue(item?.evidence || item?.excerpt || item?.content, 'Excerpt unavailable')
          const evidenceKey = `${evidenceId}-${index}`
          const isExpanded = Boolean(expandedEvidence[evidenceKey])

          return <article className="card policy-evidence-card" key={evidenceKey}>
            <span className="eyebrow">Evidence ID</span>
            <h3>{evidenceId}</h3>
            <div className="policy-evidence-meta">
              <span><strong>File:</strong> {displayValue(item?.file_name, 'Unknown file')}</span>
              <span><strong>Category:</strong> {category}</span>
              <span><strong>Source:</strong> {source}</span>
            </div>
            <EvidenceText text={excerpt} expanded={isExpanded} onToggle={() => toggleEvidenceExpansion(evidenceKey)} />
          </article>
        })}
      </div>
    ) : (
      <div className="card empty-result">
        <h3>No evidence linked to the current selection.</h3>
        <p className="muted">Retrieve station evidence or generate recommendations to view relevant authority documents.</p>
      </div>
    )}

    <section className="card policy-search-container">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Search documents</span>
          <h2>Search Policy Documents</h2>
        </div>
      </div>

      <form className="policy-search-form" onSubmit={handleSearchSubmit}>
        <input
          type="text"
          value={searchState.query}
          onChange={(event) => setSearchState((current) => ({ ...current, query: event.target.value, error: '' }))}
          placeholder="Ask about GRAP actions, pollution control measures, authorities or standards..."
          aria-label="Policy search query"
        />
        <button className="button button-primary" type="submit" disabled={searchState.loading}>
          {searchState.loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {searchState.error && <ErrorState message={searchState.error} onRetry={() => handleSearchSubmit({ preventDefault: () => {} })} />}

      {searchState.data && (
        <div className="search-summary">
          <strong>{searchState.data.total_results ?? 0}</strong>
          <span>total results</span>
        </div>
      )}

      {searchState.loading && <LoadingState label="Searching policy documents…" />}

      {searchState.data && !searchState.loading && searchResults.length === 0 && (
        <div className="card empty-result">
          <h3>No results found.</h3>
          <p className="muted">Try a broader query or a different policy topic.</p>
        </div>
      )}

      {searchResults.length > 0 && (
        <div className="policy-evidence-grid">
          {searchResults.map((item, index) => {
            const evidenceKey = `${item?.evidence_id || 'search-result'}-${index}`
            const isExpanded = Boolean(expandedEvidence[evidenceKey])
            const excerpt = displayValue(item?.evidence || item?.excerpt || item?.content, 'No evidence excerpt available')

            return <article className="card policy-evidence-card" key={evidenceKey}>
              <span className="eyebrow">Evidence</span>
              <h3>{displayValue(item?.file_name, 'Unknown file')}</h3>
              <div className="policy-evidence-meta">
                <span><strong>Category:</strong> {displayValue(item?.category, 'Unknown category')}</span>
                <span><strong>Source:</strong> {displayValue(item?.source, 'Source path unavailable')}</span>
              </div>
              <EvidenceText text={excerpt} expanded={isExpanded} onToggle={() => toggleEvidenceExpansion(evidenceKey)} />
            </article>
          })}
        </div>
      )}
    </section>

    <details className="card policy-limitations" open>
      <summary>Important limitations</summary>
      <ul>
        {limitations.map((limitation, index) => (
          <li key={`${limitation}-${index}`}>{displayValue(limitation, 'No limitation information was returned.')}</li>
        ))}
      </ul>
    </details>
  </>
}

