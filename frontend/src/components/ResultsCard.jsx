function ResultsCard({ result }) {
  if (!result) {
    return (
      <section className="panel results-panel empty">
        <p className="eyebrow">Results</p>
        <h2>No analysis yet</h2>
        <p className="muted">Run the upload flow to see OCR output, framing signals, and the scaffolded verdict.</p>
      </section>
    )
  }

  return (
    <section className="panel results-panel">
      <div className="results-header">
        <div>
          <p className="eyebrow">Results</p>
          <h2>{result.filename}</h2>
        </div>
        <span className={`risk-pill ${result.framing.overall_risk}`}>
          {result.framing.overall_risk} risk
        </span>
      </div>

      <div className="result-block">
        <h3>Article Summary</h3>
        <p>{result.article_summary}</p>
      </div>

      <div className="result-block">
        <h3>Framing Signals</h3>
        <ul className="signal-list">
          {result.framing.signals.map((signal) => (
            <li key={`${signal.label}-${signal.score}`}>
              <strong>{signal.label}.</strong> {signal.explanation}
            </li>
          ))}
        </ul>
      </div>

      <div className="result-block">
        <h3>Neutral Summary</h3>
        <p><strong>What is known:</strong> {result.neutral_summary.what_is_known}</p>
        <p><strong>What is unclear:</strong> {result.neutral_summary.what_is_unclear}</p>
        <p><strong>Takeaway:</strong> {result.neutral_summary.user_takeaway}</p>
      </div>

      <div className="result-block">
        <h3>Coverage</h3>
        {result.coverage.length === 0 ? (
          <p className="muted">No external coverage is configured yet. Connect Tavily in the backend service layer next.</p>
        ) : (
          <ul className="coverage-list">
            {result.coverage.map((item) => (
              <li key={`${item.outlet}-${item.title}`}>
                <p>
                  <strong>{item.outlet}:</strong> {item.title}
                </p>
                <p className="muted">{item.angle}</p>
                {item.published_date ? (
                  <p className="muted">
                    <strong>Published:</strong> {item.published_date}
                  </p>
                ) : null}
                {item.url ? (
                  <p>
                    <a href={item.url} target="_blank" rel="noreferrer">
                      Read article
                    </a>
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="result-block verdict-block">
        <h3>Verdict</h3>
        <p>{result.verdict}</p>
      </div>
    </section>
  )
}

export default ResultsCard
