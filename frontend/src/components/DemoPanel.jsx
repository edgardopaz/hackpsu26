import ResultsCard from './ResultsCard'

const STEP_SEQUENCE = ['Extract', 'Analyze', 'Search', 'Rank', 'Summarize']

function DemoPanel({
  file,
  claim,
  busy,
  error,
  result,
  stepStates,
  onFileChange,
  onClaimChange,
  onSubmit,
}) {
  return (
    <section id="demo" className="demo-section" data-reveal>
      <div className="section-heading">
        <p className="mono-label">Interactive Demo</p>
        <h2>Run the pipeline on a screenshot or post link.</h2>
      </div>

      <div className="demo-grid">
        <section className="demo-panel demo-panel--input">
          <div className="demo-panel__header">
            <p className="mono-label">Input</p>
            <h3>Upload a screenshot or paste a post link</h3>
          </div>

          <label className="upload-surface" htmlFor="verity-upload">
            <svg viewBox="0 0 64 64" aria-hidden="true">
              <path
                d="M32 10l11 11h-7v19h-8V21h-7L32 10zm-16 33h32v8H16v-8z"
                fill="currentColor"
              />
            </svg>
            <span>{file ? file.name : 'Drop a screenshot here or browse your files'}</span>
            <small className="mono-label">PNG, JPG, WEBP</small>
            <input
              id="verity-upload"
              type="file"
              accept="image/*"
              onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
              disabled={busy}
            />
          </label>

          <div className="demo-divider">
            <span />
            <span className="mono-label">or</span>
            <span />
          </div>

          <label className="claim-input">
            <span className="mono-label">Paste a post URL</span>
            <textarea
              rows="5"
              placeholder="https://x.com/... or another post URL"
              value={claim}
              onChange={(event) => onClaimChange(event.target.value)}
              disabled={busy}
            />
          </label>

          {error ? <p className="error-banner">{error}</p> : null}

          <button type="button" className="hero-button hero-button--primary demo-submit" onClick={onSubmit} disabled={busy}>
            {busy ? 'Analyzing claim…' : 'Analyze claim'}
          </button>
        </section>

        <section className="demo-panel demo-panel--output">
          <div className="demo-panel__header">
            <p className="mono-label">Output</p>
            <h3>Editorial result card</h3>
          </div>

          {!busy && !result ? (
            <div className="awaiting-state">
              <span className="awaiting-state__symbol">◈</span>
              <span className="mono-label">Awaiting input</span>
            </div>
          ) : null}

          {busy ? (
            <div className="demo-progress">
              <ol className="progress-track">
                {STEP_SEQUENCE.map((step, index) => (
                  <li key={step} className={`progress-step progress-step--${stepStates[index]}`}>
                    <span className="progress-step__marker">
                      {stepStates[index] === 'done' ? '✓' : stepStates[index] === 'active' ? '◌' : '·'}
                    </span>
                    <span className="mono-label">{step}</span>
                  </li>
                ))}
              </ol>

              <div className="skeleton-stack" aria-hidden="true">
                <span className="skeleton-bar skeleton-bar--wide" />
                <span className="skeleton-bar skeleton-bar--medium" />
                <span className="skeleton-bar skeleton-bar--wide" />
                <span className="skeleton-bar skeleton-bar--short" />
              </div>
            </div>
          ) : null}

          {result && !busy ? <ResultsCard result={result} /> : null}
        </section>
      </div>
    </section>
  )
}

export default DemoPanel
