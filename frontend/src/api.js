// In dev, Vite proxies /api -> localhost:8000 (see vite.config.js).
// In Docker/production, point this at wherever the backend is reachable.
const BASE = import.meta.env.VITE_API_BASE || '/api'

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: formData })
  if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed')
  return res.json()
}

export async function listDocuments() {
  const res = await fetch(`${BASE}/documents`)
  if (!res.ok) throw new Error('Failed to load documents')
  return res.json()
}

export async function deleteDocument(docId) {
  const res = await fetch(`${BASE}/documents/${docId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete document')
  return res.json()
}

export async function askQuestion(question, docIds) {
  const res = await fetch(`${BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, doc_ids: docIds && docIds.length ? docIds : null }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Query failed')
  return res.json()
}
