function UploadZone({ file, busy, onFileChange, onSubmit }) {
  return (
    <section className="panel upload-zone">
      <div>
        <p className="eyebrow">Step 1</p>
        <h2>Upload a post or screenshot</h2>
        <p className="muted">
          Start with a single image. The backend is wired for OCR, framing analysis,
          reporting lookup, and neutral summarization.
        </p>
      </div>

      <label className="file-picker" htmlFor="upload-input">
        <span>{file ? file.name : 'Choose an image file'}</span>
        <input
          id="upload-input"
          type="file"
          accept="image/*"
          onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
          disabled={busy}
        />
      </label>

      <button type="button" className="primary-button" onClick={onSubmit} disabled={!file || busy}>
        {busy ? 'Analyzing…' : 'Analyze Upload'}
      </button>
    </section>
  )
}

export default UploadZone

