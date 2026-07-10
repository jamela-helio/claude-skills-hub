import { useState } from 'react'
import { Link } from 'react-router-dom'
import { downloadBlob, generateGwaReport } from '../api.js'

export default function GwaReport() {
  const [projectName, setProjectName] = useState('')
  const [address, setAddress] = useState('')
  const [municipality, setMunicipality] = useState('')
  const [lotCount, setLotCount] = useState('')
  const [calculatorOutputs, setCalculatorOutputs] = useState('')
  const [extraContext, setExtraContext] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [done, setDone] = useState(false)

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    setDone(false)
    let parsedOutputs = {}
    if (calculatorOutputs.trim()) {
      try {
        parsedOutputs = JSON.parse(calculatorOutputs)
      } catch (_) {
        parsedOutputs = { raw_notes: calculatorOutputs }
      }
    }
    try {
      const blob = await generateGwaReport({
        site_params: {
          project_name: projectName,
          address,
          municipality,
          proposed_lot_count: lotCount,
        },
        calculator_outputs: parsedOutputs,
        extra_context: extraContext,
      })
      downloadBlob(blob, `${(projectName || 'GWA_Report').replace(/\s+/g, '_')}_Level1_GWA.docx`)
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
        <h1>📄 GWA Level 1 Report</h1>
        <p>Feed calculator outputs and site context to Claude to draft a full NSECC-compliant Level 1 Groundwater Assessment report (.docx).</p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
          <div className="section-title">Project Details</div>
          <div className="field">
            <label>Project / subdivision name</label>
            <input type="text" value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="e.g. 15 Springhill Rd Subdivision" />
          </div>
          <div className="field">
            <label>Civic address / legal description</label>
            <input type="text" value={address} onChange={(e) => setAddress(e.target.value)} />
          </div>
          <div className="field-row">
            <div className="field">
              <label>Municipality</label>
              <input type="text" value={municipality} onChange={(e) => setMunicipality(e.target.value)} />
            </div>
            <div className="field">
              <label>Proposed lot count</label>
              <input type="number" value={lotCount} onChange={(e) => setLotCount(e.target.value)} />
            </div>
          </div>
          <button className="btn" type="button" onClick={handleGenerate} disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <span className="spinner" /> : '✨'} {loading ? 'Drafting report…' : 'Generate .docx Report'}
          </button>
          {error && <div className="alert error" style={{ marginTop: 16 }}>{error}</div>}
          {done && <div className="alert info" style={{ marginTop: 16 }}>Report generated — check your downloads.</div>}
        </div>

        <div className="glass-card">
          <div className="section-title">Calculator Outputs (paste from GWA Autofill, JSON or notes)</div>
          <textarea className="textarea-lg" value={calculatorOutputs} onChange={(e) => setCalculatorOutputs(e.target.value)} placeholder='{"C14_well_depth": 60.2, "C24_K_optimistic": 1.2, ...}' style={{ width: '100%', minHeight: 220 }} />
          <div className="section-title">Additional context (well logs summary, water chemistry, notes)</div>
          <textarea className="textarea-lg" value={extraContext} onChange={(e) => setExtraContext(e.target.value)} placeholder="Paste well log summaries, water chemistry findings, or any other site notes here…" style={{ width: '100%', minHeight: 220 }} />
        </div>
      </div>
    </div>
  )
}
