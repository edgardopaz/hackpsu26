function NavBar({ scrolled }) {
  return (
    <header className={`site-nav ${scrolled ? 'site-nav--scrolled' : ''}`}>
      <div className="site-nav__inner">
        <a href="#top" className="brand-mark">
          <span className="brand-mark__word">Verity</span>
        </a>

        

        <a
          href="https://github.com/edgardopaz/hackpsu26"
          target="_blank"
          rel="noreferrer"
          className="site-nav__cta"
        >
          Github Repo
        </a>
      </div>
    </header>
  )
}

export default NavBar
