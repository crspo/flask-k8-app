import React, { useState } from 'react'

export default function App(){
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [previewSrc, setPreviewSrc] = useState(null)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [size, setSize] = useState('medium')
  const [tab, setTab] = useState('convert') // convert | products | about
  const [printForm, setPrintForm] = useState({
    componentType: '',
    vendor: '',
    modelName: '',
    description: '',
    versionCode: '',
    verifiedBy: '',
    notes: ''
  })
  const [previewDmContent, setPreviewDmContent] = useState('')
  const [statusOpen, setStatusOpen] = useState(false)
  const [status, setStatus] = useState('Inventory')
  const statusOptions = ['Inventory','Reserved','Planned','Liquidation-prep','Spare','Others']

  // Generate DM preview for Print tab from the form fields
  const generatePrintPreview = async () => {
    setError(null)
    // Build DM content: prefer pasted content (one per line). Do NOT derive from metadata.
    const pasted = (text || '').trim()
    const dmContent = pasted
    if (!dmContent){
      setError('Please paste DM content (one per line) in the field provided below.')
      return false
    }
    setLoading(true)
    try {
      setPreviewDmContent(dmContent)

      const fd = new FormData()
      fd.append('serials', dmContent)
      fd.append('size','medium')

      const res = await fetch('/api/upload', { method: 'POST', body: fd })
      if (!res.ok) {
        try {
          const errJson = await res.json()
          const msg = errJson && (errJson.error || errJson.message)
          throw new Error(msg ? msg : `Server ${res.status}`)
        } catch {
          throw new Error(`Server ${res.status}`)
        }
      }
      const json = await res.json()
      const src = json.img_src || (json.img_base64 ? (json.img_base64.startsWith('data:') ? json.img_base64 : `data:image/png;base64,${json.img_base64}`) : null)
      setPreviewSrc(src)
      if (json.pdf_b64){
        const pdfBytes = atob(json.pdf_b64)
        const len = pdfBytes.length
        const bytes = new Uint8Array(len)
        for (let i = 0; i < len; i++) bytes[i] = pdfBytes.charCodeAt(i)
        const blob = new Blob([bytes], { type: 'application/pdf' })
        setPdfUrl(URL.createObjectURL(blob))
      }
      return true
    } catch (err) {
      setError(err.message || String(err))
      return false
    } finally {
      setLoading(false)
    }
  }

  const submit = async (e) => {
    e && e.preventDefault()
    setError(null)
    // Validate: need either file or non-empty pasted text
    if (!file && (!text || text.trim() === '')){
      setError('Please paste serials or upload a text file before converting.')
      return
    }
    setLoading(true)
    try {
      const fd = new FormData()
      if (file) fd.append('file', file)
      else fd.append('serials', text)
      fd.append('size', size)

      const res = await fetch('/api/upload', { method: 'POST', body: fd })
      if (!res.ok) {
        try {
          const errJson = await res.json()
          const msg = errJson && (errJson.error || errJson.message)
          throw new Error(msg ? msg : `Server ${res.status}`)
        } catch {
          throw new Error(`Server ${res.status}`)
        }
      }
      const json = await res.json()
  // Prefer explicit ready-to-use img_src when the server provides it; otherwise fall back to img_base64.
  const src = json.img_src || (json.img_base64 ? (json.img_base64.startsWith('data:') ? json.img_base64 : `data:image/png;base64,${json.img_base64}`) : null)
  setPreviewSrc(src)

      // create downloadable blob for PDF
      const pdfBytes = atob(json.pdf_b64)
      const len = pdfBytes.length
      const bytes = new Uint8Array(len)
      for (let i = 0; i < len; i++) bytes[i] = pdfBytes.charCodeAt(i)
      const blob = new Blob([bytes], { type: 'application/pdf' })
      setPdfUrl(URL.createObjectURL(blob))

    } catch (err) {
      setError(err.message || String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="site-header">
        <div className="brand">
          <img src="/static/text-to-dm-logo.png" alt="logo" className="logo" />
          <div className="hero">
            <h1>Text→DataMatrix</h1>
            <p className="tagline">Convert serial lists into printable DataMatrix symbols</p>
          </div>
        </div>
        <nav className="tabs">
          <button className={tab==='convert'? 'active':''} onClick={() => setTab('convert')}>Convert</button>
          <button className={tab==='products'? 'active':''} onClick={() => setTab('products')}>Products</button>
          <button className={tab==='about'? 'active':''} onClick={() => setTab('about')}>About</button>
          <button className={tab==='print'? 'active':''} onClick={() => setTab('print')}>Print</button>
        </nav>
      </header>

      <main className="container">
        {tab === 'convert' && (
          <section className="card">
            <h2>Convert text to DataMatrix</h2>
            <p className="muted">Paste serials (one per line) or upload a text file. This content is also used in the Print tab. Choose output size and click Convert.</p>

            <form onSubmit={submit} className="u-form">
              <div className="two-col">
                <div>
                  <label>Paste serials</label>
                  <textarea value={text} onChange={e => setText(e.target.value)} rows={8} placeholder="S1\nS2\nS3" />
                </div>

                <div>
                  <label>Upload text file</label>
                  <input type="file" accept="text/*" onChange={e => setFile(e.target.files[0] || null)} />

                  <div className="size">
                    <label>Output size</label>
                    <div className="size-options">
                      <label><input type="radio" name="size" value="small" checked={size==='small'} onChange={() => setSize('small')} /> Small</label>
                      <label><input type="radio" name="size" value="medium" checked={size==='medium'} onChange={() => setSize('medium')} /> Medium</label>
                      <label><input type="radio" name="size" value="large" checked={size==='large'} onChange={() => setSize('large')} /> Large</label>
                    </div>
                    <div className="size-hint muted small">
                      <div>Small — approx. 18 mm</div>
                      <div>Medium — approx. 34 mm (printed)</div>
                      <div>Large — approx. 60 mm</div>
                    </div>
                  </div>

                  <div className="actions">
                    <button type="submit" disabled={loading}>Convert</button>
                  </div>
                </div>
              </div>
            </form>

            {loading && <div className="status">Working…</div>}
            {error && <div className="error">Error: {error}</div>}

            {previewSrc && (
              <div className="preview card">
                <h3>Preview</h3>
                <img src={previewSrc} alt="preview" onLoad={() => setError(null)} onError={() => setError('Failed to load preview image')} />
                {error && <div className="error">{error}</div>}
                {pdfUrl && <p><a href={pdfUrl} download="out.pdf">Download PDF</a></p>}
              </div>
            )}
          </section>
        )}

        {tab === 'print' && (
          <section className="card print-form">
            <div className="print-actions">
              <button onClick={async () => { const ok = await generatePrintPreview(); if (ok) setTimeout(() => window.print(), 150) }}>PrintMe</button>
            </div>

            {/* Title removed for compact printing */}

            <form className="u-form" onSubmit={async (e) => { e.preventDefault(); await generatePrintPreview() }}>
              <div className="form-grid">
                <div className="form-col">
                  <div className="form-row dm-content-row">
                    <label>DM Content (one per line)</label>
                    <textarea value={text} onChange={e => setText(e.target.value)} rows={4} placeholder={"S1\nS2\nS3"} />
                  </div>
                  <div className="form-row">
                    <label>Generic Component Type</label>
                    <input value={printForm.componentType} onChange={e => setPrintForm({...printForm, componentType: e.target.value})} />
                  </div>

                  <div className="form-row">
                    <label>Component Model Vendor</label>
                    <input value={printForm.vendor} onChange={e => setPrintForm({...printForm, vendor: e.target.value})} />
                  </div>

                  <div className="form-row">
                    <label>Component Model Name</label>
                    <input value={printForm.modelName} onChange={e => setPrintForm({...printForm, modelName: e.target.value})} />
                  </div>

                  <div className="form-row">
                    <label>Component Model Description</label>
                    <textarea value={printForm.description} onChange={e => setPrintForm({...printForm, description: e.target.value})} rows={2} />
                  </div>

                  <div className="form-row">
                    <label>Component Model Version Code</label>
                    <input value={printForm.versionCode} onChange={e => setPrintForm({...printForm, versionCode: e.target.value})} />
                  </div>

                  <div className="actions">
                    <button type="submit" disabled={loading}>Update preview</button>
                    <div className={`dropdown ${statusOpen ? 'open' : ''}`}>
                      <div
                        className="badge dropdown-toggle"
                        role="button"
                        tabIndex={0}
                        onClick={() => setStatusOpen(o => !o)}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setStatusOpen(o=>!o) }}
                        aria-haspopup="listbox"
                        aria-expanded={statusOpen}
                      >
                        {status.toUpperCase()}
                      </div>
                      {statusOpen && (
                        <ul className="dropdown-menu" role="listbox">
                          {statusOptions.map(opt => (
                            <li key={opt} role="option" aria-selected={status===opt}
                                onClick={() => { setStatus(opt); setStatusOpen(false) }}>
                              {opt}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </form>

            {loading && <div className="status">Working…</div>}
            {error && <div className="error">Error: {error}</div>}

            {previewSrc && (
              <div className="print-preview">
                {(() => {
                  const source = previewDmContent && previewDmContent.trim() !== '' ? previewDmContent : ''
                  const lines = (source || '').split(/\r?\n/).map(s=>s.trim()).filter(Boolean)
                  return lines.length ? (
                    <div className="preview-count">({lines.length})</div>
                  ) : null
                })()}
                <div className="preview-body">
                  <div className="left">
                    {(() => {
                      const source = previewDmContent && previewDmContent.trim() !== '' ? previewDmContent : ''
                      const lines = (source || '').split(/\r?\n/).map(s=>s.trim()).filter(Boolean)
                      const hasLines = lines.length > 0
                      const first = hasLines ? lines[0] : ''
                      const last = lines.length > 1 ? lines[lines.length-1] : ''
                      return (
                        <>
                          {hasLines && <div className="serial-first">{first}</div>}
                          <img src={previewSrc} alt="dm" />
                          {last && <div className="serial-last">{last}</div>}
                        </>
                      )
                    })()}
                  </div>

                  {/* right column removed: do not render form fields inside the preview */}
                </div>

                {/* notes removed from preview per request */}
              </div>
            )}
          </section>
        )}

        {tab === 'products' && (
          <section className="card">
            <h2>Products</h2>
            <p>This page could list packaging, SKU info, or sample exports. It's a placeholder for product-specific features.</p>
            <ul>
              <li>Sample product A — Batch label conversion</li>
              <li>Sample product B — Serial import template</li>
            </ul>
          </section>
        )}

        {tab === 'about' && (
          <section className="card">
            <h2>About</h2>
            <p>Text→DataMatrix converts lists of serials into printable DataMatrix symbols and bundles them into a PDF for printing.</p>
            <p className="muted">Built with Flask (backend) and React + Vite (frontend). Encoder uses DataMatrix rendering on the server.</p>
          </section>
        )}
      </main>

      <footer className="site-footer">
        <div className="container small muted">&copy; {new Date().getFullYear()} Text→DataMatrix</div>
      </footer>
    </div>
  )
}
