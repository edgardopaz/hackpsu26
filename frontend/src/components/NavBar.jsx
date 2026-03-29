function NavBar({ scrolled }) {
  return (
    <header className={`site-nav ${scrolled ? 'site-nav--scrolled' : ''}`}>
      <div className="site-nav__inner">
        <a href="#top" className="brand-mark">
          <span className="brand-mark__word">Verity</span>
          <span className="brand-mark__tag">Beta</span>
        </a>

        <nav className="site-nav__links" aria-label="Primary">
          <a href="#demo">Demo</a>
          <a href="#how-it-works">How it works</a>
          <a href="#pipeline">Pipeline</a>
        </nav>

        <a href="#demo" className="site-nav__cta">
          Try it free
        </a>
      </div>
    </header>
  )
}

export default NavBar
