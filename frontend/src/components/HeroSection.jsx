function HeroSection({ stats }) {
  return (
    <section id="top" className="hero-section" data-reveal>
      <div className="hero-copy">
        <div className="eyebrow-row">
          <span className="eyebrow-row__line" aria-hidden="true" />
          <span className="mono-label">Veritas Vos Liberabit</span>
        </div>
        <h1>
          <em>The truth will set you free.</em>
        </h1>
        <h2>
          <br></br>
          Verity checks media-based claims against broader reporting, surfaces manipulative framing,
          and gives you a neutral summary you can trust faster than the feed moves.
        </h2>
    
      </div>

      <div className="hero-stats">
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
