import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import ManualLlmPanel from '../components/ManualLlmPanel.jsx'
import { composeFeasibilityTiersPrompt, renderFeasibilityTiers } from '../api.js'

const TIERS = [
  { key: 'basic', label: 'Basic', desc: 'One-page scorecard · same day' },
  { key: 'detailed', label: 'Detailed', desc: 'Written report, 6–12 pages · 2–4 days' },
  { key: 'comprehensive', label: 'Comprehensive', desc: 'Full assessment, 14–25+ pages · 4–7 days' },
]

export default function HelioTiers() {
  const [address, setAddress] = useState('')
  const [tier, setTier] = useState('detailed')
  const [files, setFiles] = useState([])

  async function handleCompose() {
    if (files.length === 0) {
      throw new Error('Upload the GIS research files first.')
    }
    return composeFeasibilityTiersPrompt(address, tier, files)
  }

  async function handleRender(responseText) {
    return renderFeasibilityTiers(address, tier, responseText)
  }

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>📊 Helio Feasibility Tiers</h1>
        <p>Choose a report tier, upload GIS research files, compose a prompt, run it in Claude yourself (no API key needed), then paste the response back in for the tiered .docx.</p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
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
        </div>

        <div className="glass-card">
          <ManualLlmPanel
            onCompose={handleCompose}
            onRender={handleRender}
            downloadFilename={`${(address || 'Feasibility_Report').replace(/\s+/g, '_')}_${tier}.docx`}
            renderLabel={`Generate ${TIERS.find((t) => t.key === tier)?.label} .docx`}
          />
        </div>
      </div>
    </div>
  )
}
