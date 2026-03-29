function ResultsCard({ result }) {
  const headerLabel = result.filename ?? result.source_url ?? 'Verity analysis'
  const verdictTone =
    result.framing.overall_risk === 'high'
      ? {
          title: 'Misleading framing detected',
          tone: 'danger',
        }
      : result.framing.overall_risk === 'medium'
        ? {
            title: 'Potential framing risk',
            tone: 'warning',
          }
        : {
            title: 'Low framing risk',
            tone: 'success',
          }

  return (
    <article className="result-card">
      <div className="result-card__header">
        <div>
          <p className="result-card__label mono-label">Latest Analysis</p>
          <h3 className="result-card__title">{headerLabel}</h3>
        </div>
        <div className={`verdict-badge verdict-badge--${verdictTone.tone}`}>
          <span className="verdict-badge__pulse" aria-hidden="true" />
          <span>{verdictTone.title}</span>
        </div>
      </div>

      {result.article_summary ? (
        <section className="result-group">
          <h4>Article Summary</h4>
          <p>{result.article_summary}</p>
        </section>
      ) : null}

      <section className="result-group">
        <h4>Framing Signals</h4>
        {result.framing?.summary ? <p>{result.framing.summary}</p> : null}
        <ul className="signal-detail-list">
          {result.framing?.signals?.map((signal) => (
            <li key={`${signal.label}-${signal.explanation.slice(0, 16)}`}>
              <h5 className="signal-detail-title">{signal.label}</h5>
              <p>{signal.explanation}</p>
            </li>
          ))}
        </ul>
      </section>

      {result.neutral_summary ? (
        <section className="result-group">
          <h4>Neutral Summary</h4>
          <div className="neutral-summary">
            <p>
              <strong>What is known:</strong> {result.neutral_summary.what_is_known}
            </p>
            <p>
              <strong>What is unclear:</strong> {result.neutral_summary.what_is_unclear}
            </p>
            <p>
              <strong>Takeaway:</strong> {result.neutral_summary.user_takeaway}
            </p>
          </div>
        </section>
      ) : null}

      <section className="result-group">
        <div className="coverage-header">
          <h4>Coverage</h4>
          <span className="mono-label">Top {result.coverage?.length || 0} sources</span>
        </div>
        {!result.coverage || result.coverage.length === 0 ? (
          <p className="muted-copy">No external coverage was returned for this claim.</p>
        ) : (
          <ol className="coverage-list">
            {result.coverage.map((item, index) => (
              <li key={`${item.outlet}-${item.title}`} className="coverage-item">
                <div className="coverage-item__meta">
                  <span className="coverage-rank mono-label">0{index + 1}</span>
                  <div>
                    <h5>{item.title}</h5>
                    <p className="muted-copy">
                      <span style={{ textTransform: 'capitalize' }}>{item.outlet}</span>
                      {item.published_date ? ` • ${item.published_date}` : ''}
                    </p>
                  </div>
                </div>
                <blockquote>{item.angle}</blockquote>
                {item.url ? (
                  <a href={item.url} target="_blank" rel="noreferrer" className="coverage-link">
                    Open article
                  </a>
                ) : null}
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="result-group verdict-copy">
        <h4>Verdict</h4>
        <p>{result.verdict}</p>
      </section>
    </article>
  )
}

export default ResultsCard
