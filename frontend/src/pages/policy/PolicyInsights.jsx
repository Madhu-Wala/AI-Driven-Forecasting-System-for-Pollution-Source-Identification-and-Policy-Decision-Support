const sectors = [
  { title: 'Transport', text: 'A future space for evidence-linked transport-sector insights.' },
  { title: 'Road Dust', text: 'A future space for evidence-linked road-dust insights.' },
  { title: 'Industry', text: 'A future space for evidence-linked industrial insights.' },
]

export default function PolicyInsights() {
  return <>
    <div className="page-intro"><div><span className="eyebrow">Policy Maker · Evidence workspace</span><h1>Policy Insights</h1><p>Evidence-based recommendations for urban air-quality management.</p></div><span className="policy-status">Coming soon</span></div>
    <section className="card policy-coming-soon">
      <span className="policy-status">Under development</span>
      <h2>Policy recommendation integration is under development</h2>
      <p>Policy recommendations and authority-document retrieval are not currently available in the application. This page will show recommendations only after a policy evidence pipeline is implemented and connected.</p>
    </section>
    <div className="page-section-heading"><div><span className="eyebrow">Reserved workspace</span><h2>Sector-specific insights</h2></div></div>
    <div className="policy-placeholder-grid">
      {sectors.map((sector) => <section className="card policy-placeholder-card" key={sector.title}>
        <span className="policy-status">Coming soon</span><h3>{sector.title}</h3><p>{sector.text}</p>
        <div className="placeholder-skeleton" aria-hidden="true"><span /><span /><span /></div>
      </section>)}
    </div>
    <section className="card policy-reference-placeholder">
      <span className="eyebrow">Evidence and references</span><h3>Government documents and supporting sources</h3>
      <p className="muted">No policy evidence has been retrieved for this page. References will be displayed here when the authority-document pipeline is available.</p>
    </section>
  </>
}
