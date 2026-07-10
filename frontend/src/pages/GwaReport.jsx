import { useState } from 'react'
import { Link } from 'react-router-dom'
import ManualLlmPanel from '../components/ManualLlmPanel.jsx'
import { composeGwaReportPrompt, renderGwaReport } from '../api.js'

export default function GwaReport() {
  const [projectName, setProjectName] = useState('')
  const [address, setAddress] = useState('')
  const [municipality, setMunicipality] = useState('')
  const [lotCount, setLotCount] = useState('')
  const [calculatorOutputs, setCalculatorOutputs] = useState('')
  const [extraContext, setExtraContext] = useState('')

  function siteParams() {
    return {
      project_name: projectName,
      address,
      municipality,
      proposed_lot_count: lotCount,
    }
  }

  function parsedCalculatorOutputs() {
    if (!calculatorOutputs.trim()) return {}
    try {
      return JSON.parse(calculatorOutputs)
    } catch (_) {
      return { raw_notes: calculatorOutputs }
    }
  }

  async function handleCompose() {
    return composeGwaReportPrompt({
      site_params: siteParams(),
      calculator_outputs: parsedCalculatorOutputs(),
      extra_context: extraContext,
    })
  }

  async function handleRender(responseText) {
    return renderGwaReport({ site_params: siteParams(), response_text: responseText })
  }

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>📄 GWA Level 1 Report</h1>
        <p>Compose a prompt from calculator outputs and site context, run it in Claude yourself (no API key needed), then paste the response back in to get a formatted .docx.</p>
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
          <div className="section-title">Calculator outputs (paste from GWA Autofill, JSON or notes)</div>
          <textarea className="textarea-lg" value={calculatorOutputs} onChange={(e) => setCalculatorOutputs(e.target.value)} placeholder='{"C14_well_depth": 60.2, "C24_K_optimistic": 1.2, ...}' style={{ width: '100%', minHeight: 160 }} />
          <div className="section-title">Additional context (well logs summary, water chemistry, notes)</div>
          <textarea className="textarea-lg" value={extraContext} onChange={(e) => setExtraContext(e.target.value)} placeholder="Paste well log summaries, water chemistry findings, or any other site notes here…" style={{ width: '100%', minHeight: 160 }} />
        </div>

        <div className="glass-card">
          <ManualLlmPanel
            onCompose={handleCompose}
            onRender={handleRender}
            downloadFilename={`${(projectName || 'GWA_Report').replace(/\s+/g, '_')}_Level1_GWA.docx`}
          />
        </div>
      </div>
    </div>
  )
}
