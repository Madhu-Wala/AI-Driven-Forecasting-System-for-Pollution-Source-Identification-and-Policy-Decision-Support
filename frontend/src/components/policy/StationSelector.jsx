
export default function StationSelector({
  stations = [],
  value,
  onChange,
  label = 'Monitoring station',
}) {
  return (
    <div className="station-selector">
      <label htmlFor="station-choice">{label}</label>

      <select
        id="station-choice"
        value={value?.stationId || ''}
        onChange={(event) =>
          onChange({
            ...value,
            stationId: event.target.value,
          })
        }
        disabled={!stations.length}
      >
        {!stations.length && (
          <option value="">No monitoring stations available</option>
        )}

        {stations.map((station) => {
          const id = station.station_id || station.station_encoded
          const name = station.station_name || station.station

          return (
            <option key={id} value={id}>
              {name}
            </option>
          )
        })}
      </select>
    </div>
  )
}
