import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import { assembleFeasibilityTiers, downloadBlob } from '../api.js'

const TIERS = [
  { key: 'basic', label: 'Basic', desc: 'One-page scorecard · same day' },
  { key: 'detailed', label: 'Detailed', desc: 'Written report, 6–12 pages · 2–4 days' },
  { key: 'comprehensive', label: 'Comprehensive', desc: 'Full assessment, 14–25+ pages · 4–7 days' },
]

export default function HelioTiers() {
  const [address, setAddress] = useState('')
  const [tier, setTier] = useState('detailed')
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [done, setDone] = useState(false)

  async function handleAssemble() {
    if (files.length === 0) {
      setError('Upload the GIS research files first.')
      return
    }
    setLoading(true)
    setError(null)
    setDone(false)
    try {
      const blob = await assembleFeasibilityTiers(address, tier, files)
      downloadBlob(blob, `${(address || 'Feasibility_Report').replace(/\s+/g, '_')}_${tier}.docx`)
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
        <h1>📊 Helio Feasibility Tiers</h1>
        <p>Choose a report tier and upload GIS research files to assemble a tier-matched feasibility report (.docx).</p>
      </div>

      <div className="glass-card" style={{ maxWidth: 640 }}>
        <div className="field">
          <label>Project address</label>
          <input type="text" value={address} onChange={(e) => setAddress(e.target.value)} placeholder="e.g. 15 Springhill Rd" />
        </div>

        <div className="field">
          <label>Report tier</label>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {TIERS.map((t) => (
              <button
                key={t.key}
                type="button"
                className={`btn${tier === t.key ? '' : ' secondary'}`}
                onClick={() => setTier(t.key)}
                style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 2, padding: '10px 16px' }}
              >
                <strong>{t.label}</strong>
                <span style={{ fontWeight: 400, fontSize: '0.72rem', opacity: 0.8 }}>{t.desc}</span>
              </button>
            ))}
          </div>
        </div>

        <Dropzone label="GIS research files (zip or individual files)" multiple onFiles={setFiles} files={files} />

        <button className="btn" type="button" onClick={handleAssemble} disabled={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>
          {loading ? <span className="spinner" /> : '✨'} {loading ? 'Assembling report…' : `Assemble ${TIERS.find((t) => t.key === tier)?.label} Report`}
        </button>
        {error && <div className="alert error" style={{ marginTop: 16 }}>{error}</div>}
        {done && <div className="alert info" style={{ marginTop: 16 }}>Report generated — check your downloads.</div>}
      </div>
    </div>
  )
}
