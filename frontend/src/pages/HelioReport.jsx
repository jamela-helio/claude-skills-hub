import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import ManualLlmPanel from '../components/ManualLlmPanel.jsx'
import { composeFeasibilityReportPrompt, renderFeasibilityReport } from '../api.js'

export default function HelioReport() {
  const [address, setAddress] = useState('')
  const [files, setFiles] = useState([])

  async function handleCompose() {
    if (files.length === 0) {
      throw new Error('Upload a zip (or the individual GIS/architectural files) first.')
    }
    return composeFeasibilityReportPrompt(address, files)
  }

  async function handleRender(responseText) {
    return renderFeasibilityReport(address, responseText)
  }

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>🏗️ Helio Pre-Dev Report</h1>
        <p>Upload a zip of GIS research and architectural drawings, compose a prompt, run it in Claude yourself (no API key needed), then paste the response back in for a polished .docx.</p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
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
        </div>

        <div className="glass-card">
          <ManualLlmPanel
            onCompose={handleCompose}
            onRender={handleRender}
            downloadFilename={`${(address || 'Pre_Development_Assessment').replace(/\s+/g, '_')}.docx`}
          />
        </div>
      </div>
    </div>
  )
}
