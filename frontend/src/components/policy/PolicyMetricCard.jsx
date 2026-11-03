export default function PolicyMetricCard({ label, value, detail, tone = 'blue' }) {
  return <article className={`card policy-metric policy-metric-${tone}`}>
    <span className="eyebrow">{label}</span>
    <strong>{value ?? 'Unavailable'}</strong>
    {detail && <span className="policy-metric-detail">{detail}</span>}
  </article>
}
