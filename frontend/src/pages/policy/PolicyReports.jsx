import { useEffect, useMemo, useState } from 'react'
import ErrorState from '../../components/ErrorState'
import LoadingState from '../../components/LoadingState'
import StationSelector from '../../components/policy/StationSelector'
import TimeSeriesChart from '../../components/policy/TimeSeriesChart'
import { getPolicyStations, getStationAnalytics } from '../../services/policyService'

const PAGE_SIZE = 25
const series = [
  { field: 'aqi', title: 'Historical AQI', unit: 'AQI' },
  { field: 'pm25', title: 'PM2.5', unit: 'µg/m³' },
  { field: 'pm10', title: 'PM10', unit: 'µg/m³' },
  { field: 'no2', title: 'NO₂', unit: 'µg/m³' },
  { field: 'so2', title: 'SO₂', unit: 'µg/m³' },
  { field: 'co', title: 'CO', unit: 'µg/m³' },
  { field: 'o3', title: 'O₃', unit: 'µg/m³' },
]

function formatTimestamp(value) {
  return value ? new Date(value).toLocaleString() : 'Unavailable'
}

export default function PolicyReports() {
  const [selection, setSelection] = useState({ stationId: '', search: '' })
  const [stations, setStations] = useState({ data: [], loading: true, error: '' })
  const [history, setHistory] = useState({ data: null, loading: false, error: '' })
  const [page, setPage] = useState(0)

  useEffect(() => {
    let active = true
    const timer = setTimeout(() => {
      getPolicyStations()
        .then((response) => {
          if (!active) return
          const records = response.stations || []
          setStations({ data: records, loading: false, error: '' })
          if (records.length) {
            setSelection((current) => ({
              ...current,
              stationId: current.stationId || records[0].station_id,
            }))
          }
        })
        .catch((error) => {
          console.error(error)
          if (active) setStations({ data: [], loading: false, error: error.message || 'Unable to load monitoring stations.' })
        })
    }, 0)
    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [])

  useEffect(() => {
    if (!selection.stationId) return undefined
    let active = true
    const timer = setTimeout(() => {
      setHistory({ data: null, loading: true, error: '' })
      setPage(0)
      getStationAnalytics(selection.stationId)
        .then((data) => {
          if (active) setHistory({ data, loading: false, error: '' })
        })
        .catch((error) => {
          console.error(error)
          if (active) setHistory({ data: null, loading: false, error: error.message || 'Unable to load station history.' })
        })
    }, 0)
    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [selection.stationId])

  const data = useMemo(() => history.data?.data || [], [history.data])
  const availableFields = useMemo(() => new Set(
    (history.data?.available_pollutants || []).filter((field) => data.some((record) => record[field] != null && record[field] !== '' && Number.isFinite(Number(record[field])))),
  ), [history.data, data])
  const latestFirst = [...data].reverse()
  const pageCount = Math.ceil(latestFirst.length / PAGE_SIZE)
  const pageRecords = latestFirst.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return <>
    <div className="page-intro"><div><span className="eyebrow">Policy Maker · Historical data</span><h1>Reports</h1><p>Review the station history returned by the air-quality analytics service.</p></div>{history.data?.period && <span className="policy-status">{history.data.period.replaceAll('_', ' ')}</span>}</div>
    <section className="card policy-report-toolbar">
      <StationSelector stations={stations.data} value={selection} onChange={setSelection} label="Choose a station" />
      {history.data && <div className="report-meta"><span>{history.data.station_name || history.data.station_id}</span><span>{history.data.total_records ?? data.length} returned records</span><span>Interval: {history.data.interval || 'Unavailable'}</span><span>Timezone: {history.data.timezone || 'Unavailable'}</span></div>}
    </section>
    {stations.loading && <LoadingState label="Loading station list…" />}
    {stations.error && <ErrorState message={stations.error} />}
    {history.loading && <LoadingState label="Loading historical records…" />}
    {history.error && <ErrorState message={history.error} />}
    {!history.loading && !history.error && history.data && <>
      {!data.length && <div className="card empty-result"><h3>No historical records returned</h3><p className="muted">The analytics API returned no records for this station and period.</p></div>}
      {!!data.length && <>
        <div className="page-section-heading"><div><span className="eyebrow">Observed history</span><h2>Historical trends</h2></div></div>
        <div className="report-chart-grid">
          {series.filter((item) => availableFields.has(item.field)).map((item) => <TimeSeriesChart key={item.field} {...item} data={data} />)}
        </div>
        <section className="card report-table-card">
          <div className="section-heading"><div><span className="eyebrow">API records</span><h3>Historical data table</h3></div><span className="chart-unit">{history.data.timezone || 'Timezone unavailable'}</span></div>
          <div className="report-table-scroll">
            <table className="report-table">
              <thead><tr><th>Timestamp</th>{series.filter((item) => availableFields.has(item.field)).map((item) => <th key={item.field}>{item.title}</th>)}</tr></thead>
              <tbody>{pageRecords.map((record, index) => <tr key={`${record.timestamp}-${index}`}><td>{formatTimestamp(record.timestamp)}</td>{series.filter((item) => availableFields.has(item.field)).map((item) => <td key={item.field}>{record[item.field] != null && record[item.field] !== '' && Number.isFinite(Number(record[item.field])) ? Number(record[item.field]).toFixed(2) : '—'}</td>)}</tr>)}</tbody>
            </table>
          </div>
          <div className="report-pagination"><span>{latestFirst.length ? `${page * PAGE_SIZE + 1}–${Math.min((page + 1) * PAGE_SIZE, latestFirst.length)} of ${latestFirst.length} records` : 'No records'}</span><div><button className="button button-quiet" disabled={!page} onClick={() => setPage((current) => current - 1)}>Previous</button><button className="button button-quiet" disabled={page >= pageCount - 1} onClick={() => setPage((current) => current + 1)}>Next</button></div></div>
        </section>
      </>}
    </>}
    <p className="muted policy-report-note">This report displays recorded data only. It does not evaluate policy impact or infer that an intervention changed pollution levels.</p>
  </>
}
