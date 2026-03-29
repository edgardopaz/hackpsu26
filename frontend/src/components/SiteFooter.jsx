function SiteFooter() {
  return (
    <footer className="site-footer" data-reveal>
      <div>
        <p className="brand-mark__word">Verity</p>
      </div>
      <div>
        <p className="mono-label">Tech stack</p>
        <p>FastAPI + Gemini + Tavily + React/Vite</p>
      </div>
      <div className="site-footer__right">
        <p className="mono-label">Hackathon demo</p>
        <p>Built for rapid verification under pressure.</p>
      </div>
    </footer>
  )
}

export default SiteFooter
