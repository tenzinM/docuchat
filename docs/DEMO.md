# Demo Walkthrough

A step-by-step walkthrough of DocuChat in action, using a sample document about a
fictional company ("Acme Robotics") to illustrate the flow end-to-end.

> This is a written walkthrough. Once you've run the app yourself, replace this file
> (or supplement it) with a real `demo.gif` screen recording — see the "Recording your
> own demo" section at the bottom.

---

## 1. Upload a document

Open the app at `http://localhost:5173`. The left panel shows the document list and
an upload dropzone.

```
┌─────────────────────────────┐
│  Documents                   │
│                               │
│  ┌─────────────────────────┐ │
│  │  Click to upload a PDF  │ │
│  └─────────────────────────┘ │
│                               │
│  No documents yet.           │
└─────────────────────────────┘
```

After selecting a PDF (e.g. `acme_robotics_overview.pdf`), the file is sent to
`POST /upload`. The backend extracts text page-by-page, splits it into overlapping
chunks, embeds each chunk locally, and stores it in ChromaDB.

**Expected response:**
```json
{
  "doc_id": "a1b2c3d4e5f6",
  "filename": "acme_robotics_overview.pdf",
  "num_chunks": 2,
  "message": "Document ingested successfully."
}
```

The document list updates immediately:

```
┌─────────────────────────────┐
│  Documents                   │
│                               │
│  ☐ acme_robotics_overview.pdf│
│     2 chunks              ✕  │
└─────────────────────────────┘
```

## 2. Ask a question

Type a question into the chat input, e.g.:

> **"Who is the CEO of Acme Robotics?"**

This triggers `POST /query`. The backend:
1. Embeds the question
2. Retrieves the most similar chunks from ChromaDB (in this case, the chunk from
   page 2 containing the CEO's name)
3. Builds a grounded prompt with numbered source labels
4. Sends it to the local Ollama model
5. Returns the answer plus the raw source chunks used

**Expected response:**
```json
{
  "answer": "The CEO of Acme Robotics is Jane Whitfield [1].",
  "sources": [
    {
      "doc_id": "a1b2c3d4e5f6",
      "filename": "acme_robotics_overview.pdf",
      "chunk_index": 1,
      "page": 2,
      "text": "Page two continues the document. The CEO of Acme Robotics is Jane Whitfield. The company has offices in Toronto and Austin.",
      "similarity": 0.87
    }
  ],
  "used_context": true
}
```

**Rendered in the UI:**

```
┌───────────────────────────────────────────────┐
│  Who is the CEO of Acme Robotics?              │
│                                                  │
│  The CEO of Acme Robotics is Jane Whitfield [1].│
│                                                  │
│  [ Show sources (1) ]                           │
└───────────────────────────────────────────────┘
```

## 3. Expand the citation

Clicking "Show sources" reveals exactly which passage the answer was grounded in —
this is the transparency feature that separates DocuChat from a plain chatbot wrapper:

```
┌───────────────────────────────────────────────┐
│  [1] acme_robotics_overview.pdf — page 2        │
│      similarity 0.87                            │
│                                                  │
│  "Page two continues the document. The CEO of   │
│  Acme Robotics is Jane Whitfield. The company    │
│  has offices in Toronto and Austin."            │
└───────────────────────────────────────────────┘
```

## 4. Ask something the document doesn't cover

> **"What is Acme Robotics' stock ticker symbol?"**

Since no chunk in the document contains this information, retrieval either returns
low-similarity chunks or none at all, and the model — instructed to refuse rather than
guess — responds:

```json
{
  "answer": "I couldn't find that in the provided document(s).",
  "sources": [],
  "used_context": false
}
```

This refusal behavior is the single most important reliability property of the
pipeline: a model that stays silent on missing information is far more trustworthy
than one that fills gaps with plausible-sounding guesses.

## 5. Restrict search to specific documents

If multiple PDFs are uploaded, checking one or more boxes in the document list scopes
retrieval to only those documents (`doc_ids` filter on `/query`) — useful for comparing
or isolating sources when you have several files loaded at once.

---

## Recording your own demo GIF

Once you've run this locally with real documents:

1. **Mac:** [Kap](https://getkap.co/) (free, exports GIF directly)
2. **Windows:** [ScreenToGif](https://www.screentogif.com/) (free)
3. **Linux:** [Peek](https://github.com/phw/peek) (free)

Suggested recording (10–15 seconds is plenty):
1. Upload a PDF (2–3 sec)
2. Type and submit a question (3–4 sec)
3. Let the answer render (2–3 sec)
4. Click "Show sources" to reveal the citation (2–3 sec)

Save the result as `docs/demo.gif` — the README's `![DocuChat demo](docs/demo.gif)`
line already points at that path, so it'll render automatically once the file exists.
