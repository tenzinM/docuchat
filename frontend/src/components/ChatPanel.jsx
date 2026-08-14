import { useState } from 'react'
import { askQuestion } from '../api'
import SourcesPanel from './SourcesPanel'

export default function ChatPanel({ selectedIds }) {
  const [question, setQuestion] = useState('')
  const [history, setHistory] = useState([]) // {question, answer, sources, usedContext}
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleAsk(e) {
    e.preventDefault()
    if (!question.trim() || loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await askQuestion(question, selectedIds)
      setHistory((h) => [...h, { question, answer: res.answer, sources: res.sources, usedContext: res.used_context }])
      setQuestion('')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel chat-panel">
      <h2>Ask a question</h2>

      <div className="chat-history">
        {history.length === 0 && (
          <p className="empty">Upload a document and ask something about it.</p>
        )}
        {history.map((turn, i) => (
          <div className="chat-turn" key={i}>
            <div className="chat-question">{turn.question}</div>
            <div className="chat-answer">{turn.answer}</div>
            {turn.usedContext && <SourcesPanel sources={turn.sources} />}
          </div>
        ))}
        {loading && <div className="chat-turn loading">Thinking…</div>}
      </div>

      {error && <p className="error">{error}</p>}

      <form onSubmit={handleAsk} className="chat-input-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask something about your document(s)…"
        />
        <button type="submit" disabled={loading}>Ask</button>
      </form>
    </div>
  )
}
