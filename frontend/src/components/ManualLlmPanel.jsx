import { useState } from 'react'
import { downloadBlob } from '../api.js'

/**
 * Shared "no API key needed" flow for the LLM-assisted tools:
 * 1. Compose the full prompt (skill instructions + your inputs) server-side.
 * 2. You copy it into Claude.ai or Claude Code and run it yourself.
 * 3. Paste Claude's response back in — either to download a .docx (onRender)
 *    or just to copy the finished text (when onRender is omitted, e.g. Land
 *    Use Prompt Builder, whose whole output IS the thing you copy).
 */
export default function ManualLlmPanel({ onCompose, onRender, downloadFilename, renderLabel = 'Generate .docx' }) {
  const [prompt, setPrompt] = useState('')
  const [responseText, setResponseText] = useState('')
  const [composing, setComposing] = useState(false)
  const [rendering, setRendering] = useState(false)
  const [error, setError] = useState(null)
  const [copiedPrompt, setCopiedPrompt] = useState(false)
  const [copiedResponse, setCopiedResponse] = useState(false)
  const [done, setDone] = useState(false)

  async function handleCompose() {
    setComposing(true)
    setError(null)
    setPrompt('')
    setDone(false)
    try {
      const { prompt } = await onCompose()
      setPrompt(prompt)
    } catch (e) {
      setError(e.message)
    } finally {
      setComposing(false)
    }
  }

  function handleCopyPrompt() {
    navigator.clipboard?.writeText(prompt)
    setCopiedPrompt(true)
    setTimeout(() => setCopiedPrompt(false), 1500)
  }

  function handleCopyResponse() {
    navigator.clipboard?.writeText(responseText)
    setCopiedResponse(true)
    setTimeout(() => setCopiedResponse(false), 1500)
  }

  async function handleRender() {
    if (!onRender) return
    setRendering(true)
    setError(null)
    setDone(false)
    try {
      const blob = await onRender(responseText)
      downloadBlob(blob, downloadFilename)
      setDone(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setRendering(false)
    }
  }

  return (
    <div>
      <button className="btn" type="button" onClick={handleCompose} disabled={composing} style={{ width: '100%', justifyContent: 'center' }}>
        {composing ? <span className="spinner" /> : '📋'} {composing ? 'Composing prompt…' : '1. Compose Prompt'}
      </button>
      {error && <div className="alert error" style={{ marginTop: 16 }}>{error}</div>}

      {prompt && (
        <>
          <div className="alert info" style={{ marginTop: 16 }}>
            Copy this prompt into <strong>Claude.ai</strong> or <strong>Claude Code</strong> and run it there
            (free under your existing plan — no API key needed). Then paste Claude's response back in below.
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '12px 0 6px' }}>
            <span className="section-title" style={{ margin: 0 }}>Prompt to copy</span>
            <button className="btn secondary" type="button" onClick={handleCopyPrompt}>
              {copiedPrompt ? '✓ Copied' : '⧉ Copy Prompt'}
            </button>
          </div>
          <div className="prompt-output">{prompt}</div>

          <div className="section-title">2. Paste Claude's response here</div>
          <textarea
            className="textarea-lg"
            style={{ width: '100%', minHeight: 260 }}
            value={responseText}
            onChange={(e) => setResponseText(e.target.value)}
            placeholder="Paste Claude's full response here…"
          />

          {onRender ? (
            <button
              className="btn"
              type="button"
              onClick={handleRender}
              disabled={rendering || !responseText.trim()}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {rendering ? <span className="spinner" /> : '⬇'} {rendering ? 'Rendering…' : `3. ${renderLabel}`}
            </button>
          ) : (
            <button
              className="btn secondary"
              type="button"
              onClick={handleCopyResponse}
              disabled={!responseText.trim()}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {copiedResponse ? '✓ Copied' : '⧉ Copy Final Result'}
            </button>
          )}
          {done && <div className="alert info" style={{ marginTop: 16 }}>Done — check your downloads.</div>}
        </>
      )}
    </div>
  )
}
