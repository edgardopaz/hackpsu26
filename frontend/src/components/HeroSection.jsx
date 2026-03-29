function HeroSection({ stats }) {
  return (
    <section id="top" className="hero-section" data-reveal>
      <div className="hero-grid-lines" aria-hidden="true" />
      <div className="hero-copy">
        <div className="eyebrow-row">
          <span className="eyebrow-row__line" aria-hidden="true" />
          <span className="mono-label">Real-time verification</span>
        </div>
        <h1>
          The truth, <em>sourced</em> in seconds.
        </h1>
        <p className="hero-copy__body">
          Verity checks screenshot-based claims against broader reporting, surfaces manipulative framing,
          and gives you a neutral summary you can trust faster than the feed moves.
        </p>
        <div className="hero-actions">
          <a href="#demo" className="hero-button hero-button--primary">
            Try the demo →
          </a>
          <a href="#pipeline" className="hero-button hero-button--ghost">
            See the pipeline
          </a>
        </div>
      </div>

      <div className="hero-stats" data-reveal>
        {stats.map((stat, index) => (
          <div key={stat.label} className="hero-stat" style={{ '--stagger': `${index * 0.1}s` }}>
            <span className="hero-stat__value">{stat.value}</span>
            <span className="hero-stat__label mono-label">{stat.label}</span>
          </div>
        ))}
      </div>
    </section>
  )
}

export default HeroSection
