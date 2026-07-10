// In dev, Vite proxies /api to the local FastAPI server (see vite.config.js).
// In production (Vercel), set VITE_API_BASE_URL to the deployed backend's
// origin, e.g. https://claude-skills-hub-api.onrender.com
const API_ORIGIN = import.meta.env.VITE_API_BASE_URL || ''
const BASE = `${API_ORIGIN}/api`

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      detail = data.detail || JSON.stringify(data)
    } catch (_) {
      /* ignore */
    }
    throw new Error(detail)
  }
  return res
}

export async function gwaAutofill(siteParams, files) {
  const form = new FormData()
  form.append('site_params', JSON.stringify(siteParams))
  Object.entries(files).forEach(([key, file]) => {
    if (file) form.append(key, file)
  })
  const res = await fetch(`${BASE}/gwa/autofill`, { method: 'POST', body: form })
  await handle(res)
  return res.json()
}

export async function generateGwaReport(payload) {
  const res = await fetch(`${BASE}/gwa/report/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  await handle(res)
  return res.blob()
}

export async function composeGwaReportPrompt(payload) {
  const res = await fetch(`${BASE}/gwa/report/compose-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  await handle(res)
  return res.json()
}

export async function renderGwaReport(payload) {
  const res = await fetch(`${BASE}/gwa/report/render`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  await handle(res)
  return res.blob()
}

export async function assembleFeasibilityReport(projectAddress, files) {
  const form = new FormData()
  form.append('project_address', projectAddress)
  files.forEach((f) => form.append('files', f))
  const res = await fetch(`${BASE}/feasibility-report/assemble`, { method: 'POST', body: form })
  await handle(res)
  return res.blob()
}

export async function composeFeasibilityReportPrompt(projectAddress, files) {
  const form = new FormData()
  form.append('project_address', projectAddress)
  files.forEach((f) => form.append('files', f))
  const res = await fetch(`${BASE}/feasibility-report/compose-prompt`, { method: 'POST', body: form })
  await handle(res)
  return res.json()
}

export async function renderFeasibilityReport(projectAddress, responseText) {
  const res = await fetch(`${BASE}/feasibility-report/render`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_address: projectAddress, response_text: responseText }),
  })
  await handle(res)
  return res.blob()
}

export async function assembleFeasibilityTiers(projectAddress, tier, files) {
  const form = new FormData()
  form.append('project_address', projectAddress)
  form.append('tier', tier)
  files.forEach((f) => form.append('files', f))
  const res = await fetch(`${BASE}/feasibility-tiers/assemble`, { method: 'POST', body: form })
  await handle(res)
  return res.blob()
}

export async function composeFeasibilityTiersPrompt(projectAddress, tier, files) {
  const form = new FormData()
  form.append('project_address', projectAddress)
  form.append('tier', tier)
  files.forEach((f) => form.append('files', f))
  const res = await fetch(`${BASE}/feasibility-tiers/compose-prompt`, { method: 'POST', body: form })
  await handle(res)
  return res.json()
}

export async function renderFeasibilityTiers(projectAddress, tier, responseText) {
  const res = await fetch(`${BASE}/feasibility-tiers/render`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_address: projectAddress, tier, response_text: responseText }),
  })
  await handle(res)
  return res.blob()
}

export async function populateHtmlCards(dataText) {
  const form = new FormData()
  form.append('data_text', dataText)
  const res = await fetch(`${BASE}/html-populator/populate`, { method: 'POST', body: form })
  await handle(res)
  return res.json()
}

export async function composeLubLookupPrompt(zoneCode, municipality, question) {
  const res = await fetch(`${BASE}/lub-lookup/compose-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ zone_code: zoneCode, municipality, question }),
  })
  await handle(res)
  return res.json()
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
