import { useEffect, useMemo, useRef, useState } from 'react'
import { analyzePost } from './api/client'
import DemoPanel from './components/DemoPanel'
import HeroSection from './components/HeroSection'
import NavBar from './components/NavBar'
import PipelineSection from './components/PipelineSection'
import SiteFooter from './components/SiteFooter'

const STEP_SEQUENCE = ['Extract', 'Analyze', 'Search', 'Rank', 'Summarize']
const STEP_DELAYS = [400, 700, 900, 600, 800]

function App() {
  const [file, setFile] = useState(null)
  const [claim, setClaim] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [stepStates, setStepStates] = useState(() => STEP_SEQUENCE.map(() => 'idle'))
  const [navScrolled, setNavScrolled] = useState(false)
  const abortControllerRef = useRef(null)

  useEffect(() => {
    const onScroll = () => {
      setNavScrolled(window.scrollY > 24)
    }

    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible')
            observer.unobserve(entry.target)
          }
        }
      },
      { threshold: 0.18, rootMargin: '0px 0px -5% 0px' },
    )

    const elements = document.querySelectorAll('[data-reveal]')
    elements.forEach((element) => observer.observe(element))

    return () => observer.disconnect()
  }, [])

  const stats = useMemo(
    () => [
      { value: '~3.2s', label: 'avg analysis time' },
      { value: '3', label: 'ranked live sources' },
      { value: '5-stage', label: 'verification pipeline' },
    ],
    [],
  )

  function validateInput() {
    if (!file && !claim.trim()) {
      return 'Upload a screenshot or paste a post link to run the demo.'
    }

    if (file && claim.trim()) {
      return 'Choose one input mode: upload a screenshot or paste a link.'
    }

    if (claim.trim()) {
      try {
        new URL(claim.trim())
      } catch {
        return 'For the text field, paste a valid post URL. For plain text claims, use a screenshot for now.'
      }
    }

    return ''
  }

  async function runProgressSimulation(signal) {
    setStepStates(STEP_SEQUENCE.map(() => 'idle'))

    for (let index = 0; index < STEP_SEQUENCE.length; index += 1) {
      if (signal?.aborted) return

      setStepStates((current) =>
        current.map((_, currentIndex) => {
          if (currentIndex < index) return 'done'
          if (currentIndex === index) return 'active'
          return 'idle'
        }),
      )

      await new Promise((resolve) => {
        const timerId = window.setTimeout(resolve, STEP_DELAYS[index])
        if (signal) {
          signal.addEventListener(
            'abort',
            () => {
              window.clearTimeout(timerId)
              resolve()
            },
            { once: true },
          )
        }
      })

      if (signal?.aborted) return

      setStepStates((current) =>
        current.map((state, currentIndex) => (currentIndex <= index ? 'done' : state)),
      )
    }
  }

  async function handleAnalyze() {
    const validationError = validateInput()
    if (validationError) {
      setError(validationError)
      return
    }

    abortControllerRef.current?.abort()
    const abortController = new AbortController()
    abortControllerRef.current = abortController

    setBusy(true)
    setError('')
    setResult(null)

    try {
      const [response] = await Promise.all([
        analyzePost(file, claim.trim()),
        runProgressSimulation(abortController.signal),
      ])
      if (!abortController.signal.aborted) {
        setResult(response)
      }
    } catch (requestError) {
      if (!abortController.signal.aborted) {
        abortController.abort()
        setError(requestError.message || 'An error occurred during analysis.')
        setStepStates(STEP_SEQUENCE.map(() => 'idle'))
      }
    } finally {
      if (abortControllerRef.current === abortController) {
        setBusy(false)
      }
    }
  }

  return (
    <>
      <div className="noise-overlay" aria-hidden="true" />
      <div className="floating-orb orb-gold" aria-hidden="true" />
      <div className="floating-orb orb-red" aria-hidden="true" />

      <NavBar scrolled={navScrolled} />

      <main className="page-shell">
        <HeroSection stats={stats} />

        <DemoPanel
          file={file}
          claim={claim}
          busy={busy}
          error={error}
          result={result}
          stepStates={stepStates}
          onFileChange={setFile}
          onClaimChange={setClaim}
          onSubmit={handleAnalyze}
        />

        <PipelineSection />
        <SiteFooter />
      </main>
    </>
  )
}

export default App
