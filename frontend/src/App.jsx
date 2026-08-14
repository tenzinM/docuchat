import { useEffect, useState, useCallback } from 'react'
import UploadPanel from './components/UploadPanel'
import ChatPanel from './components/ChatPanel'
import { listDocuments, deleteDocument } from './api'

export default function App() {
  const [documents, setDocuments] = useState([])
  const [selectedIds, setSelectedIds] = useState([])

  const refresh = useCallback(async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (e) {
      console.error(e)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  function toggleSelect(docId) {
    setSelectedIds((ids) =>
      ids.includes(docId) ? ids.filter((id) => id !== docId) : [...ids, docId]
    )
  }

  async function handleDelete(docId) {
    await deleteDocument(docId)
    setSelectedIds((ids) => ids.filter((id) => id !== docId))
    refresh()
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>DocuChat</h1>
        <p>Ask questions about your PDFs — answered locally, grounded with citations.</p>
      </header>
      <main className="app-main">
        <UploadPanel
          documents={documents}
          onUploaded={refresh}
          onDelete={handleDelete}
          selectedIds={selectedIds}
          onToggleSelect={toggleSelect}
        />
        <ChatPanel selectedIds={selectedIds} />
      </main>
    </div>
  )
}
