import { useRef, useState } from 'react'

export default function Dropzone({ label, hint, multiple = false, accept, onFiles, files }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const selected = multiple ? files || [] : files ? [files] : []

  function handleFiles(fileList) {
    const arr = Array.from(fileList)
    onFiles(multiple ? arr : arr[0])
  }

  function removeAt(idx) {
    if (multiple) {
      const next = [...selected]
      next.splice(idx, 1)
      onFiles(next)
    } else {
      onFiles(null)
    }
  }

  return (
    <div className="field">
      <label>{label}</label>
      <div
        className={`dropzone${dragging ? ' dragging' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          handleFiles(e.dataTransfer.files)
        }}
      >
        {hint || 'Drag & drop, or click to browse'}
        <input
          ref={inputRef}
          type="file"
          multiple={multiple}
          accept={accept}
          hidden
          onChange={(e) => e.target.files.length && handleFiles(e.target.files)}
        />
      </div>
      {selected.length > 0 && (
        <div className="dropzone-list">
          {selected.map((f, idx) => (
            <div className="dropzone-item" key={f.name + idx}>
              <span>✓ {f.name}</span>
              <button className="remove" onClick={() => removeAt(idx)} type="button">
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
