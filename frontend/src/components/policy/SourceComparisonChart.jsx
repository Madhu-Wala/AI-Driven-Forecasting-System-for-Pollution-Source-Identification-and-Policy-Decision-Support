const sectors = [
  { key: 'traffic', label: 'Transport' },
  { key: 'road_dust_construction', label: 'Road Dust' },
  { key: 'industry', label: 'Industry' },
]

export default function SourceComparisonChart({ scores = {} }) {
  const values = sectors.map((sector) => scores[sector.key])
  const maxMagnitude = Math.max(...values.filter(Number.isFinite).map(Math.abs), 1)

  return <div className="source-comparison" role="img" aria-label="Horizontal comparison of signed source anomaly scores with a zero baseline">
    {sectors.map((sector) => {
      const value = scores[sector.key]
      const available = Number.isFinite(value)
      const width = available ? `${Math.abs(value) / maxMagnitude * 50}%` : '0%'
      return <div className="source-bar-row" key={sector.key}>
        <span className="source-bar-label">{sector.label}</span>
        <div className="source-bar-track">
          <span className="source-zero-line" />
          {available && <span
            className={`source-bar ${value < 0 ? 'source-bar-negative' : 'source-bar-positive'}`}
            style={value < 0 ? { width, right: '50%' } : { width, left: '50%' }}
          />}
        </div>
        <strong className="source-bar-value">{available ? value.toFixed(3) : 'Unavailable'}</strong>
      </div>
    })}
    <p className="source-chart-caption">Signed anomaly score · zero marks the historical baseline</p>
  </div>
}
