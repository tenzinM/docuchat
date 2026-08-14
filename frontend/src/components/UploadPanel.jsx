import { useRef, useState } from 'react'
import { uploadDocument } from '../api'

export default function UploadPanel({ documents, onUploaded, onDelete, selectedIds, onToggleSelect }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef()

  async function handleFile(file) {
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      await uploadDocument(file)
      onUploaded()
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div className="panel">
      <h2>Documents</h2>

      <label className="dropzone">
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          onChange={(e) => handleFile(e.target.files[0])}
          hidden
        />
        {uploading ? 'Uploading…' : 'Click to upload a PDF'}
      </label>

      {error && <p className="error">{error}</p>}

      <ul className="doc-list">
        {documents.map((doc) => (
          <li key={doc.doc_id} className={selectedIds.includes(doc.doc_id) ? 'selected' : ''}>
            <label>
              <input
                type="checkbox"
                checked={selectedIds.includes(doc.doc_id)}
                onChange={() => onToggleSelect(doc.doc_id)}
              />
              <span className="doc-name">{doc.filename}</span>
              <span className="doc-meta">{doc.num_chunks} chunks</span>
            </label>
            <button className="delete-btn" onClick={() => onDelete(doc.doc_id)} title="Delete">
              ✕
            </button>
          </li>
        ))}
        {documents.length === 0 && <li className="empty">No documents yet.</li>}
      </ul>
      <p className="hint">
        {selectedIds.length === 0
          ? 'No documents selected — questions search across all uploaded documents.'
          : `Searching only within ${selectedIds.length} selected document(s).`}
      </p>
    </div>
  )
}
