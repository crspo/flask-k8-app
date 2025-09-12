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

  const submit = async (e) => {
    e && e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const fd = new FormData()
      if (file) fd.append('file', file)
      else fd.append('serials', text)
      fd.append('size', size)

  const res = await fetch('/api/upload', { method: 'POST', body: fd })
  if (!res.ok) throw new Error(`Server returned ${res.status}`)
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
        </nav>
      </header>

      <main className="container">
        {tab === 'convert' && (
          <section className="card">
            <h2>Convert text to DataMatrix</h2>
            <p className="muted">Paste serials (one per line) or upload a text file. Choose output size and click Convert.</p>

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
