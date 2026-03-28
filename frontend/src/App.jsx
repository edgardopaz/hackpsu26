import { useEffect, useState } from 'react'
import { analyzePost } from './api/client'
import ProgressSteps from './components/ProgressSteps'
import ResultsCard from './components/ResultsCard'
import UploadZone from './components/UploadZone'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [link, setLink] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    if (!busy) {
      return undefined
    }

    const timer = window.setInterval(() => {
      setActiveStep((current) => (current < 3 ? current + 1 : current))
    }, 700)

    return () => window.clearInterval(timer)
  }, [busy])

  function handleModeChange(newMode) {
    // Clear the opposite mode's state when switching
    if (newMode === 'screenshot') {
      setLink('')
    } else {
      setFile(null)
    }
  }

  async function handleAnalyze() {
    // Validation
    if (!file && !link) {
      setError('Please provide either a screenshot or a social media link.')
      return
    }

    if (file && link) {
      setError('Please provide either a screenshot or a link, not both.')
      return
    }

    setBusy(true)
    setError('')
    setResult(null)
    setActiveStep(0)

    try {
      const response = await analyzePost(file, link)
      setResult(response)
      setActiveStep(4)
    } catch (requestError) {
      setError(requestError.message || 'An error occurred during analysis.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">Fact Checker</p>
        <h1>Verify screenshot-driven claims before the framing does the work for you.</h1>
        <p className="hero-copy">
          Upload a post, detect manipulative framing, compare it against broader reporting,
          and return a more neutral explanation of what is actually being said.
        </p>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}

      <section className="dashboard-grid">
        <UploadZone
          file={file}
          link={link}
          busy={busy}
          onFileChange={setFile}
          onLinkChange={setLink}
          onModeChange={handleModeChange}
          onSubmit={handleAnalyze}
        />
        <ProgressSteps activeStep={activeStep} busy={busy} />
        <ResultsCard result={result} />
      </section>
    </main>
  )
}

export default App
