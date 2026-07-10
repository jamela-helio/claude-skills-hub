import { useState } from 'react'
import { Link } from 'react-router-dom'
import Dropzone from '../components/Dropzone.jsx'
import ManualLlmPanel from '../components/ManualLlmPanel.jsx'
import { composeLandUsePrompt } from '../api.js'

export default function LandUsePrompt() {
  const [files, setFiles] = useState([])

  async function handleCompose() {
    if (files.length === 0) {
      throw new Error('Upload at least one planning document (PDF, deed, map, or screenshot).')
    }
    return composeLandUsePrompt(files)
  }

  return (
    <div>
      <Link className="back-link" to="/">
        ← Dashboard
      </Link>
      <div className="page-header">
        <h1>📝 Land Use Prompt Builder</h1>
        <p>
          Upload planning documents, deeds, maps, or screenshots. This composes a prompt that reads them and rebuilds the
          standardized Land Use Feasibility Report prompt — run it in Claude yourself (no API key needed), then copy the
          result straight from there.
        </p>
      </div>

      <div className="tool-layout">
        <div className="glass-card">
          <Dropzone label="Planning documents (PDFs, deeds, maps, screenshots)" multiple onFiles={setFiles} files={files} />
        </div>

        <div className="glass-card">
          <ManualLlmPanel onCompose={handleCompose} />
        </div>
      </div>
    </div>
  )
}
