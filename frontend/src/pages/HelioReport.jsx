import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import { assembleFeasibilityReport, downloadBlob } from '../api.js'

export default function HelioReport() {
  const [address, setAddress] = useState('')
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [done, setDone] = useState(false)

  async function handleAssemble() {
    if (files.length === 0) {
      setError('Upload a zip (or the individual GIS/architectural files) first.')
      return
    }
    setLoading(true)
    setError(null)
    setDone(false)
    try {
      const blob = await assembleFeasibilityReport(address, files)
      downloadBlob(blob, `${(address || 'Pre_Development_Assessment').replace(/\s+/g, '_')}.docx`)
      setDone(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>🏗️ Helio Pre-Dev Report</h1>
        <p>Upload a zip containing GIS research and architectural drawings to assemble a polished Pre-Development Site Assessment report (.docx).</p>
      </div>

      <div className="glass-card" style={{ maxWidth: 640 }}>
        <div className="field">
          <label>Project address</label>
          <input type="text" value={address} onChange={(e) => setAddress(e.target.value)} placeholder="e.g. 14 Holland Ave, Bedford" />
        </div>
        <Dropzone
          label="GIS research + architectural drawings (zip or individual files)"
          hint="Drop a .zip, or the GIS Summary Report, maps, and site plans directly"
          multiple
          onFiles={setFiles}
          files={files}
        />
        <button className="btn" type="button" onClick={handleAssemble} disabled={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>
          {loading ? <span className="spinner" /> : '✨'} {loading ? 'Assembling report…' : 'Assemble Report'}
        </button>
        {error && <div className="alert error" style={{ marginTop: 16 }}>{error}</div>}
        {done && <div className="alert info" style={{ marginTop: 16 }}>Report generated — check your downloads.</div>}
      </div>
    </div>
  )
}
