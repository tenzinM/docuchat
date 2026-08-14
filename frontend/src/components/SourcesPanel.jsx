import { useState } from 'react'

export default function SourcesPanel({ sources }) {
  const [open, setOpen] = useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div className="sources-panel">
      <button className="sources-toggle" onClick={() => setOpen(!open)}>
        {open ? 'Hide' : 'Show'} sources ({sources.length})
      </button>
      {open && (
        <div className="sources-list">
          {sources.map((s, i) => (
            <div className="source-chunk" key={i}>
              <div className="source-meta">
                [{i + 1}] {s.filename} — page {s.page} — similarity {s.similarity}
              </div>
              <div className="source-text">{s.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
