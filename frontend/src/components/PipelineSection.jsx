const PIPELINE_STEPS = [
  {
    number: '01',
    symbol: '⬡',
    title: 'Extract',
    description: 'Turn the uploaded file or link into usable text.',
    tech: 'Gemini Vision',
  },
  {
    number: '02',
    symbol: '◎',
    title: 'Analyze',
    description: 'Detect manipulative framing or bait-like language.',
    tech: 'Gemini 2.5',
  },
  {
    number: '03',
    symbol: '⊕',
    title: 'Search',
    description: 'Compare the claim against broader reporting.',
    tech: 'Tavily API',
  },
  {
    number: '04',
    symbol: '◈',
    title: 'Rank',
    description: 'Keep only the most relevant sources and trim noisy snippets.',
    tech: 'Custom scoring',
  },
  {
    number: '05',
    symbol: '◇',
    title: 'Summarize',
    description: 'Produce a neutral explanation of what is known and unclear.',
    tech: 'Gemini 2.5',
  },
]

function PipelineSection() {
  return (
    <section id="pipeline" className="pipeline-section" data-reveal>
      <div className="section-heading" id="how-it-works">
        <p className="mono-label">How it works</p>
        <h2>Five linked stages, one faster verification loop.</h2>
      </div>

      <div className="pipeline-grid">
        {PIPELINE_STEPS.map((step) => (
          <article key={step.number} className="pipeline-card" data-reveal>
            <span className="pipeline-card__number mono-label">{step.number}</span>
            <span className="pipeline-card__symbol" aria-hidden="true">
              {step.symbol}
            </span>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
            <span className="pipeline-card__tech mono-label">{step.tech}</span>
          </article>
        ))}
      </div>
    </section>
  )
}

export default PipelineSection
