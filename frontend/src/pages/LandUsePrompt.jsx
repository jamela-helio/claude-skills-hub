import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import { extractLandUsePrompt } from '../api.js'

export default function LandUsePrompt() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [prompt, setPrompt] = useState('')
  const [copied, setCopied] = useState(false)

  async function handleExtract() {
    if (files.length === 0) {
      setError('Upload at least one planning document (PDF, deed, map, or screenshot).')
      return
    }
    setLoading(true)
    setError(null)
    setPrompt('')
    try {
      const data = await extractLandUsePrompt(files)
      setPrompt(data.prompt)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function handleCopy() {
    navigator.clipboard?.writeText(prompt)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>📝 Land Use Prompt Builder</h1>
        <p>Upload planning documents, deeds, maps, or screenshots to extract project details and rebuild the standardized Land Use Feasibility Report prompt.</p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
          <Dropzone label="Planning documents (PDFs, deeds, maps, screenshots)" multiple onFiles={setFiles} files={files} />
          <button className="btn" type="button" onClick={handleExtract} disabled={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>
            {loading ? <span className="spinner" /> : '✨'} {loading ? 'Extracting…' : 'Build Prompt'}
          </button>
          {error && <div className="alert error" style={{ marginTop: 16 }}>{error}</div>}
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div className="section-title" style={{ margin: 0 }}>
              Generated Prompt
            </div>
            {prompt && (
              <button className="btn secondary" type="button" onClick={handleCopy}>
                {copied ? '✓ Copied' : '⧉ Copy'}
              </button>
            )}
          </div>
          {prompt ? <div className="prompt-output">{prompt}</div> : <div className="alert info">The completed prompt will appear here, ready to copy.</div>}
        </div>
      </div>
    </div>
  )
}
