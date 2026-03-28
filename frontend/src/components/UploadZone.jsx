import { useState } from 'react'

function UploadZone({ file, link, busy, onFileChange, onLinkChange, onModeChange, onSubmit }) {
  const [mode, setMode] = useState('screenshot')
  const [urlError, setUrlError] = useState('')

  const handleModeChange = (newMode) => {
    setMode(newMode)
    setUrlError('')
    if (onModeChange) {
      onModeChange(newMode)
    }
  }

  const handleLinkChange = (value) => {
    onLinkChange(value)
    setUrlError('')
  }

  const handleLinkBlur = () => {
    if (link && !isValidUrl(link)) {
      setUrlError('Please enter a valid URL')
    }
  }

  const isValidUrl = (url) => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const isSubmitDisabled = () => {
    if (busy) return true
    if (mode === 'screenshot') return !file
    if (mode === 'link') return !link || !isValidUrl(link)
    return true
  }

  return (
    <section className="panel upload-zone">
      <div>
        <p className="eyebrow">Step 1</p>
        <h2>Upload a post or screenshot</h2>
        <p className="muted">
          Choose a social media post by uploading a screenshot or providing a direct link.
          The backend will extract text using OCR or by fetching post metadata.
        </p>
      </div>

      <div className="mode-toggle">
        <button
          type="button"
          className={`mode-button ${mode === 'screenshot' ? 'active' : ''}`}
          onClick={() => handleModeChange('screenshot')}
          disabled={busy}
          title="Upload a screenshot of a social media post"
        >
          📸 Screenshot
        </button>
        <button
          type="button"
          className={`mode-button ${mode === 'link' ? 'active' : ''}`}
          onClick={() => handleModeChange('link')}
          disabled={busy}
          title="Provide a direct link to a social media post"
        >
          🔗 Post Link
        </button>
      </div>

      {mode === 'screenshot' ? (
        <label className="file-picker" htmlFor="upload-input">
          <span>{file ? file.name : 'Choose an image file'}</span>
          <input
            id="upload-input"
            type="file"
            accept="image/*"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
            disabled={busy}
            aria-label="Upload screenshot"
          />
        </label>
      ) : (
        <div className="link-input-wrapper">
          <input
            id="post-link-input"
            type="url"
            placeholder="https://twitter.com/... or https://facebook.com/..."
            value={link}
            onChange={(event) => handleLinkChange(event.target.value)}
            onBlur={handleLinkBlur}
            disabled={busy}
            className="link-input"
            aria-label="Social media post URL"
          />
          {urlError && <p className="input-error">{urlError}</p>}
        </div>
      )}

      <button
        type="button"
        className="primary-button"
        onClick={onSubmit}
        disabled={isSubmitDisabled()}
        title={isSubmitDisabled() ? 'Please provide valid input to analyze' : 'Click to analyze the post'}
      >
        {busy ? 'Analyzing…' : 'Analyze Upload'}
      </button>
    </section>
  )
}

export default UploadZone

