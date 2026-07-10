import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import { populateHtmlCards } from '../api.js'

const SAMPLE = `# --- Parcel ---
pid: 41146804
address: 257 Main St\\nYarmouth, NS
area_m2: 362.3 m²
area_ft2: 3,900 ft²
zone: R-3
zone_desc: Multiple Family Residential-Medium Density

# --- Geology / Environmental ---
groundwater: Metamorphic
surficial_geology: Stony, sandy matrix, material derived from local bedrock sources
vs30: 813 m/s (Class B: Rock)
surface_form: Level
karst_risk: Low
flood_risk: Moderate
soil_drainage: Well and Moderately Well
dtw: 4 m
saltwater: no data
site_condition: Dry area, suitable for most uses with low risk of sogginess
topography: Flat to rolling, with many surface boulders.

# --- Utilities ---
min_setback: 2 m (Centre Plan Package B)
service_req: Urban Service Area
stormwater: Halifax Water
sewershed: Halifax WWTF
distribution: J. Douglas Kline (Pockwock) Water Supply Plant
`

function downloadText(filename, text) {
  const blob = new Blob([text], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function HtmlPopulator() {
  const [dataText, setDataText] = useState(SAMPLE)
  const [dataFile, setDataFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  async function handleRun() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      let text = dataText
      if (dataFile) {
        text = await dataFile.text()
      }
      const data = await populateHtmlCards(text)
      setResult(data)
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
        <h1>🧩 HTML Layout Card Populator</h1>
        <p>Paste or upload a key:value data file to populate the parcelinfo, Environmental, and Utilities QGIS layout HTML cards.</p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
          <div className="section-title">Data File</div>
          <Dropzone label="Upload a .txt data file (optional)" onFiles={setDataFile} files={dataFile} accept=".txt" />
          <div className="field">
            <label>Or paste key: value data directly</label>
            <textarea className="textarea-lg" style={{ minHeight: 320, width: '100%' }} value={dataText} onChange={(e) => setDataText(e.target.value)} />
          </div>
          <button className="btn" type="button" onClick={handleRun} disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <span className="spinner" /> : '⚡'} {loading ? 'Populating…' : 'Populate Cards'}
          </button>
          {error && <div className="alert error" style={{ marginTop: 16 }}>{error}</div>}
        </div>

        <div>
          {!result && <div className="glass-card alert info">Populated card previews will appear here.</div>}
          {result &&
            Object.entries(result.templates).map(([name, tpl]) => (
              <div className="glass-card" key={name} style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <div className="section-title" style={{ margin: 0 }}>
                    {name} {tpl.found ? `· ${tpl.fields_injected} fields injected` : '· not found'}
                  </div>
                  {tpl.found && (
                    <button className="btn secondary" type="button" onClick={() => downloadText(name, tpl.html)}>
                      ⬇ Download
                    </button>
                  )}
                </div>
                {tpl.found ? (
                  <iframe title={name} srcDoc={tpl.html} style={{ width: '100%', height: 340, border: '1px solid var(--border-glass)', borderRadius: 10, background: '#fff' }} />
                ) : (
                  <div className="alert error">Template not found on server.</div>
                )}
                {tpl.unrecognised_keys?.length > 0 && (
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 8 }}>
                    Unrecognised keys skipped: {tpl.unrecognised_keys.join(', ')}
                  </p>
                )}
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}
