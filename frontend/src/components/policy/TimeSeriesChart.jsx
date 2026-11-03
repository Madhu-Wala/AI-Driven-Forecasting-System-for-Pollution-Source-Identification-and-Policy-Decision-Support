export default function TimeSeriesChart({ title, data = [], field, unit = '' }) {
  const points = data
    .map((record) => ({ timestamp: record.timestamp, value: record[field] }))
    .filter((point) => point.timestamp && point.value != null && point.value !== '' && Number.isFinite(Number(point.value)))

  if (!points.length) {
    return <section className="card report-chart">
      <h3>{title}</h3>
      <p className="muted">No {title.toLowerCase()} values are available for this station.</p>
    </section>
  }

  const width = 720
  const height = 220
  const padding = { top: 20, right: 24, bottom: 32, left: 52 }
  const values = points.map((point) => Number(point.value))
  const rawMin = Math.min(...values)
  const rawMax = Math.max(...values)
  const spread = rawMax - rawMin || Math.max(Math.abs(rawMax) * 0.1, 1)
  const min = rawMin - spread * 0.08
  const max = rawMax + spread * 0.08
  const plotWidth = width - padding.left - padding.right
  const plotHeight = height - padding.top - padding.bottom
  const coordinates = points.map((point, index) => ({
    ...point,
    x: padding.left + (points.length === 1 ? plotWidth / 2 : index / (points.length - 1) * plotWidth),
    y: padding.top + (max - Number(point.value)) / (max - min) * plotHeight,
  }))
  const path = coordinates.map((point, index) => `${index ? 'L' : 'M'} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(' ')
  const firstDate = new Date(points[0].timestamp).toLocaleDateString()
  const lastDate = new Date(points.at(-1).timestamp).toLocaleDateString()

  return <section className="card report-chart">
    <div className="section-heading"><h3>{title}</h3><span className="chart-unit">{unit}</span></div>
    <div className="chart-scroll">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${title} historical trend from ${firstDate} to ${lastDate}`}>
        {[0, 0.5, 1].map((fraction) => {
          const y = padding.top + fraction * plotHeight
          const label = (max - fraction * (max - min)).toFixed(1)
          return <g key={fraction}>
            <line x1={padding.left} x2={width - padding.right} y1={y} y2={y} className="chart-grid-line" />
            <text x={padding.left - 8} y={y + 4} textAnchor="end" className="chart-axis-label">{label}</text>
          </g>
        })}
        <path d={path} fill="none" className="chart-series-line" />
        {coordinates.length < 50 && coordinates.map((point, index) => <circle key={`${point.timestamp}-${index}`} cx={point.x} cy={point.y} r="3" className="chart-series-point"><title>{new Date(point.timestamp).toLocaleString()}: {Number(point.value).toFixed(2)} {unit}</title></circle>)}
        <text x={padding.left} y={height - 8} className="chart-axis-label">{firstDate}</text>
        <text x={width - padding.right} y={height - 8} textAnchor="end" className="chart-axis-label">{lastDate}</text>
      </svg>
    </div>
    <p className="chart-observation-count">{points.length} returned observations</p>
  </section>
}
