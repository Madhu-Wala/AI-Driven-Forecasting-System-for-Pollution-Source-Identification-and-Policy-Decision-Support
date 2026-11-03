export default function StationSelector({ stations = [], value, onChange, label = 'Monitoring station' }) {
  const matches = stations.filter((station) => {
    const name = station.station_name || station.station || ''
    return name.toLowerCase().includes((value?.search || '').toLowerCase())
  })
  const selectedIsVisible = matches.some((station) => String(station.station_id || station.station_encoded) === String(value?.stationId || ''))

  return <div className="station-selector">
    <label htmlFor="station-search">{label}</label>
    <input
      id="station-search"
      type="search"
      placeholder="Search stations"
      value={value?.search || ''}
      onChange={(event) => onChange({ ...value, search: event.target.value })}
      autoComplete="off"
    />
    <label className="visually-hidden" htmlFor="station-choice">Select a station</label>
    <select
      id="station-choice"
      value={selectedIsVisible ? value.stationId : ''}
      onChange={(event) => onChange({ ...value, stationId: event.target.value })}
      disabled={!matches.length}
    >
      {!selectedIsVisible && <option value="">{matches.length ? 'Select a matching station' : 'No matching stations'}</option>}
      {matches.map((station) => {
        const id = station.station_id || station.station_encoded
        const name = station.station_name || station.station
        return <option key={id} value={id}>{name}</option>
      })}
    </select>
    {!stations.length && <span className="muted">No monitoring stations are available.</span>}
  </div>
}
