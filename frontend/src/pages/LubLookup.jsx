import { useState } from 'react'
import { Link } from 'react-router-dom'
import ManualLlmPanel from '../components/ManualLlmPanel.jsx'
import { composeLubLookupPrompt } from '../api.js'

export default function LubLookup() {
  const [zoneCode, setZoneCode] = useState('')
  const [municipality, setMunicipality] = useState('')
  const [question, setQuestion] = useState('')

  async function handleCompose() {
    if (!zoneCode.trim() || !municipality.trim()) {
      throw new Error('Enter both a zone code and a municipality / plan area.')
    }
    return composeLubLookupPrompt(zoneCode, municipality, question)
  }

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>⚖️ NS LUB Lookup</h1>
        <p>
          Look up zoning requirements for any zone code and municipality in Nova Scotia. Composes a prompt with the
          bundled LUB index — run it in Claude yourself, ideally with web search (or the Google Drive MCP) enabled,
          since this skill depends on live lookups against the actual bylaw text.
        </p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
          <div className="field">
            <label>Zone code</label>
            <input type="text" value={zoneCode} onChange={(e) => setZoneCode(e.target.value)} placeholder="e.g. HR-1, R-2, ER-3" />
          </div>
          <div className="field">
            <label>Municipality / plan area</label>
            <input
              type="text"
              value={municipality}
              onChange={(e) => setMunicipality(e.target.value)}
              placeholder="e.g. Regional Centre, Bedford, Lunenburg County"
            />
          </div>
          <div className="field">
            <label>Specific question (optional — leave blank for a full zone summary)</label>
            <textarea
              className="textarea-lg"
              style={{ width: '100%', minHeight: 120 }}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. What is the minimum front setback? Is a duplex allowed? Is this in a flood zone?"
            />
          </div>
        </div>

        <div className="glass-card">
          <ManualLlmPanel onCompose={handleCompose} />
        </div>
      </div>
    </div>
  )
}
