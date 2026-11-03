const sectors = [
  { key: 'traffic', title: 'Transport', pollutants: 'NO₂ and CO', icon: '↔' },
  { key: 'road_dust_construction', title: 'Road Dust', pollutants: 'PM10 and coarse PM', icon: '⌁' },
  { key: 'industry', title: 'Industry', pollutants: 'SO₂', icon: '▥' },
]

function formatScore(value) {
  return Number.isFinite(value) ? value.toFixed(3) : 'Unavailable'
}

export default function SourceScoreCard({ scores = {}, labels = {} }) {
  return <div className="source-score-grid">
    {sectors.map((sector) => {
      const score = scores[sector.key]
      const status = labels[sector.key] || 'Insufficient data'
      const tone = score > 0 ? 'above' : score < 0 ? 'below' : Number.isFinite(score) ? 'around' : 'unknown'
      return <article className={`card source-score-card source-score-${tone}`} key={sector.key}>
        <div className="source-score-heading">
          <span className="source-sector-icon" aria-hidden="true">{sector.icon}</span>
          <div><span className="eyebrow">Source Anomaly Score</span><h3>{sector.title}</h3></div>
        </div>
        <strong className="source-score-value">{formatScore(score)}</strong>
        <span className={`source-signal-label signal-${tone}`}>{status}</span>
        <span className="source-pollutants">Associated signals: {sector.pollutants}</span>
      </article>
    })}
  </div>
}
