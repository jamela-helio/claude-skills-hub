import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import { gwaAutofill } from '../api.js'

const ZONING_PRESETS = [
  { label: 'AP-1 / AP-2 / AR-3 (West Hants, unserviced)', minLotArea: 4000 },
  { label: 'R-1 (HRM, serviced)', minLotArea: 371 },
  { label: 'R-2 (HRM, semi, serviced)', minLotArea: 278 },
  { label: 'RR — Rural Residential', minLotArea: 6000 },
  { label: 'RC', minLotArea: 2000 },
  { label: 'Custom', minLotArea: null },
]

function copyToClipboard(text) {
  navigator.clipboard?.writeText(String(text ?? ''))
}

export default function GwaAutofill() {
  const [params, setParams] = useState({
    site_area_m2: '',
    ground_elev_avg: '',
    ground_elev_min: '',
    county: '',
    bedrock_hu: '',
    zoning_preset: ZONING_PRESETS[0].label,
    min_lot_area_m2: ZONING_PRESETS[0].minLotArea,
    infra_deduction_pct: 0.3,
    wet_exclusion_pct: 0,
  })
  const [files, setFiles] = useState({
    well_logs: null,
    pumping_tests: null,
    water_chemistry: null,
    observation_well: null,
    climate_normals: null,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  function updateParam(key, value) {
    setParams((p) => ({ ...p, [key]: value }))
  }

  function onZoningChange(label) {
    const preset = ZONING_PRESETS.find((z) => z.label === label)
    setParams((p) => ({
      ...p,
      zoning_preset: label,
      min_lot_area_m2: preset?.minLotArea ?? p.min_lot_area_m2,
    }))
  }

  async function handleSubmit() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const numericParams = {
        ...params,
        site_area_m2: params.site_area_m2 ? Number(params.site_area_m2) : null,
        ground_elev_avg: params.ground_elev_avg ? Number(params.ground_elev_avg) : null,
        ground_elev_min: params.ground_elev_min ? Number(params.ground_elev_min) : null,
        min_lot_area_m2: params.min_lot_area_m2 ? Number(params.min_lot_area_m2) : null,
        infra_deduction_pct: Number(params.infra_deduction_pct),
        wet_exclusion_pct: Number(params.wet_exclusion_pct),
      }
      const data = await gwaAutofill(numericParams, files)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const dc = result?.dual_constraint
  const maxScale = dc ? Math.max(dc.net_lots_zoning || 0, dc.net_lots_gw_low || 0, dc.net_lots_gw_high || 0, 1) : 1

  const inputRows = result
    ? [
        ['C14', 'Well depth (m)', result.well_logs?.C14_well_depth],
        ['C15', 'Casing length (m)', result.well_logs?.C15_casing_length],
        ['C16', 'Well diameter (m)', result.well_logs?.C16_well_diameter],
        ['C18', 'Seasonal fluctuation (m)', result.observation_well?.C18_seasonal_fluctuation],
        ['C23', 'Static WL (mbgs)', result.well_logs?.C23_static_wl],
        ['C24', 'K optimistic (m/d)', result.pumping_tests?.C24_K_optimistic],
        ['C25', 'K average (m/d)', result.pumping_tests?.C25_K_average],
        ['C26', 'K pessimistic (m/d)', result.pumping_tests?.C26_K_pessimistic],
        ['C27', 'Storativity S', result.pumping_tests?.C27_storativity],
        ['C33', 'Annual precipitation (mm/y)', result.climate_normals?.C33_precipitation_mm],
      ]
    : []

  const allFlags = [
    ...(result?.well_logs?.flags || []),
    ...(result?.pumping_tests?.flags || []),
    ...(result?.observation_well?.flags || []),
    ...(result?.climate_normals?.flags || []),
    ...(dc?.level2_gwa_notes || []),
  ]

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>💧 GWA Calculator Autofill</h1>
        <p>Upload the standard NS data files and site parameters to auto-fill the Level 1 GWA Yield Calculator INPUTS sheet, plus the zoning-vs-recharge dual constraint check.</p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
          <div className="section-title">Site Parameters</div>
          <div className="field">
            <label>Site area (m²)</label>
            <input type="number" value={params.site_area_m2} onChange={(e) => updateParam('site_area_m2', e.target.value)} placeholder="e.g. 12000" />
          </div>
          <div className="field-row">
            <div className="field">
              <label>Avg elevation (masl)</label>
              <input type="number" value={params.ground_elev_avg} onChange={(e) => updateParam('ground_elev_avg', e.target.value)} />
            </div>
            <div className="field">
              <label>Min elevation (masl)</label>
              <input type="number" value={params.ground_elev_min} onChange={(e) => updateParam('ground_elev_min', e.target.value)} />
            </div>
          </div>
          <div className="field-row">
            <div className="field">
              <label>County</label>
              <input type="text" value={params.county} onChange={(e) => updateParam('county', e.target.value)} placeholder="e.g. Halifax" />
            </div>
            <div className="field">
              <label>Bedrock HU code</label>
              <input type="text" value={params.bedrock_hu} onChange={(e) => updateParam('bedrock_hu', e.target.value)} placeholder="e.g. ME, GR, WI" />
            </div>
          </div>
          <div className="field">
            <label>Zoning</label>
            <select value={params.zoning_preset} onChange={(e) => onZoningChange(e.target.value)}>
              {ZONING_PRESETS.map((z) => (
                <option key={z.label} value={z.label}>
                  {z.label}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Min lot area (m²)</label>
            <input type="number" value={params.min_lot_area_m2 ?? ''} onChange={(e) => updateParam('min_lot_area_m2', e.target.value)} />
          </div>
          <div className="field-row">
            <div className="field">
              <label>Infrastructure deduction ({Math.round(params.infra_deduction_pct * 100)}%)</label>
              <input type="range" min="0" max="0.6" step="0.01" value={params.infra_deduction_pct} onChange={(e) => updateParam('infra_deduction_pct', e.target.value)} />
            </div>
            <div className="field">
              <label>WAM wet exclusion ({Math.round(params.wet_exclusion_pct * 100)}%)</label>
              <input type="range" min="0" max="0.6" step="0.01" value={params.wet_exclusion_pct} onChange={(e) => updateParam('wet_exclusion_pct', e.target.value)} />
            </div>
          </div>

          <div className="section-title">Site Data Files</div>
          <Dropzone label="Well_logs.csv" onFiles={(f) => setFiles((s) => ({ ...s, well_logs: f }))} files={files.well_logs} accept=".csv" />
          <Dropzone label="Pumping_tests.csv" onFiles={(f) => setFiles((s) => ({ ...s, pumping_tests: f }))} files={files.pumping_tests} accept=".csv" />
          <Dropzone label="Water_chemistry.csv" onFiles={(f) => setFiles((s) => ({ ...s, water_chemistry: f }))} files={files.water_chemistry} accept=".csv" />
          <Dropzone label="Observation Well (*.xls)" onFiles={(f) => setFiles((s) => ({ ...s, observation_well: f }))} files={files.observation_well} accept=".xls" />
          <Dropzone label="Canadian_Climate_Normals.csv" onFiles={(f) => setFiles((s) => ({ ...s, climate_normals: f }))} files={files.climate_normals} accept=".csv" />

          <button className="btn" type="button" onClick={handleSubmit} disabled={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>
            {loading ? <span className="spinner" /> : '⚡'} {loading ? 'Computing…' : 'Run Autofill'}
          </button>
        </div>

        <div>
          {error && <div className="alert error">{error}</div>}
          {!result && !error && <div className="glass-card alert info">Upload at least one data file and click Run Autofill to see computed calculator inputs here.</div>}

          {result && (
            <>
              <div className="glass-card" style={{ marginBottom: 20 }}>
                <div className="section-title">Calculator INPUTS Table</div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Cell</th>
                      <th>Field</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inputRows.map(([cell, label, value]) => (
                      <tr key={cell}>
                        <td>{cell}</td>
                        <td>{label}</td>
                        <td className="copyable" title="Click to copy" onClick={() => copyToClipboard(value)}>
                          {value ?? '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {allFlags.length > 0 && (
                  <ul className="flag-list">
                    {allFlags.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                )}
              </div>

              {result.water_chemistry?.rows?.length > 0 && (
                <div className="glass-card" style={{ marginBottom: 20 }}>
                  <div className="section-title">Water Quality (GCDWQ) Summary</div>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Parameter</th>
                        <th>Type</th>
                        <th>Limit</th>
                        <th>n</th>
                        <th># Exceeding</th>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.water_chemistry.rows.map((r) => (
                        <tr key={r.column}>
                          <td>{r.parameter}</td>
                          <td>{r.type}</td>
                          <td>{r.limit}</td>
                          <td>{r.n_samples}</td>
                          <td>{r.n_exceeding}</td>
                          <td>{r.min}</td>
                          <td>{r.max}</td>
                          <td style={{ color: r.status === 'OK' ? 'var(--accent-green)' : 'var(--accent-red)' }}>{r.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {dc && (
                <div className="glass-card">
                  <div className="section-title">Dual Constraint — Zoning vs. Groundwater Recharge</div>
                  <div className="constraint-panel">
                    <div className={`constraint-box${dc.binding_conservative_by === 'Zoning area' ? ' binding' : ''}`}>
                      {dc.binding_conservative_by === 'Zoning area' && <span className="binding-badge">BINDING</span>}
                      <div className="label">Zoning Area Limit</div>
                      <div className="value">{dc.net_lots_zoning ?? '—'}</div>
                      <div className="bar-track">
                        <div className="bar-fill" style={{ width: `${((dc.net_lots_zoning || 0) / maxScale) * 100}%` }} />
                      </div>
                    </div>
                    <div className={`constraint-box${dc.binding_conservative_by === 'GW recharge' ? ' binding' : ''}`}>
                      {dc.binding_conservative_by === 'GW recharge' && <span className="binding-badge">BINDING</span>}
                      <div className="label">GW Recharge Limit (conservative)</div>
                      <div className="value">{dc.net_lots_gw_low ?? '—'}</div>
                      <div className="bar-track">
                        <div className="bar-fill" style={{ width: `${((dc.net_lots_gw_low || 0) / maxScale) * 100}%` }} />
                      </div>
                    </div>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 16 }}>
                    Optimistic GW recharge limit: <strong style={{ color: 'var(--text-primary)' }}>{dc.net_lots_gw_high ?? '—'}</strong> lots ·
                    Average lot size at binding count: <strong style={{ color: 'var(--text-primary)' }}>{dc.avg_lot_size_m2 ?? '—'} m²</strong> ({dc.avg_lot_size_acres ?? '—'} ac)
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
