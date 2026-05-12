# 🇫🇮 Helppoa

Helppoa is a local retrieval-augmented generation (RAG) prototype for answering questions from uploaded documents. Upload a PDF, TXT, or Markdown file through the web UI, then ask questions grounded in the document's content. Everything runs locally with Ollama, Mistral, LangChain, and ChromaDB.

## ✨ Features

- 🖥️ **Web UI** — React + TypeScript frontend with file upload and chat interface
- ⚡ **FastAPI backend** — REST API with `/upload`, `/ask`, `/status`, and `/reset` endpoints
- 📄 **Local document ingestion** for `.pdf`, `.txt`, and `.md` files (up to 25 MB)
- 🔍 Chunking with overlap for better retrieval context
- 🧮 Local embeddings through Ollama (`nomic-embed-text`)
- 💾 Persistent local vector storage with ChromaDB
- 💬 Extractive chat responses through `ChatOllama` (`mistral`)
- ⚡ In-memory LLM response cache for repeated identical prompts
- 🖥️ Interactive **CLI mode** available via `rag.py`

## 📋 Requirements

- Python 3.11 or newer
- Node.js 18+ and npm (for the frontend)
- Ollama installed and running
- The `mistral` Ollama model (chat / generation)
- The `nomic-embed-text` Ollama model (embeddings)

Install the Ollama models:

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

## 🚀 Setup

### Backend

Create a virtual environment and install Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend

Install Node dependencies:

```bash
cd frontend
npm install
```

## ▶️ Running the App

### Option 1: Web UI (recommended)

Start the FastAPI backend and the Vite dev server in two terminals:

```bash
# Terminal 1 — API server
venv/bin/uvicorn api.main:app --reload

# Terminal 2 — Frontend dev server
cd frontend && npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser. The Vite dev server proxies `/api/*` requests to the FastAPI backend automatically.

### Option 2: CLI mode

```bash
./venv/bin/python rag.py
```

## 🔌 API Endpoints

| Method | Path      | Description                          |
|--------|-----------|--------------------------------------|
| GET    | `/status` | Returns indexing status and metadata |
| POST   | `/upload` | Upload a document for ingestion      |
| POST   | `/ask`    | Ask a question about the indexed doc |
| POST   | `/reset`  | Clear the current session and index  |

## ⚙️ Configuration

The app works with defaults, but these environment variables can override them:

```bash
export DOCUMENT_PATH="data/helppoa_test_reference.pdf"
export DB_PATH="db/chroma_ollama"
export OLLAMA_MODEL="mistral"
export OLLAMA_EMBED_MODEL="nomic-embed-text"
```

## 📁 Project Structure

```text
helppoa/
├── api/
│   ├── __init__.py
│   ├── main.py            # FastAPI app — routes and middleware
│   └── rag_service.py     # HTTP-friendly RAG pipeline wrapper
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBox.tsx
│   │   │   └── FileUpload.tsx
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── main.tsx
│   │   ├── styles.css
│   │   └── types.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── data/
├── rag.py                 # Core RAG pipeline + CLI
├── requirements.txt
└── README.md
```

`db/chroma_ollama/` is created at runtime and ignored by Git. Uploaded files are written to a system temp directory during indexing and deleted immediately after.

## 🔄 How It Works

```text
source document
  -> load
  -> split into chunks
  -> embed with Ollama
  -> store in Chroma

user question
  -> embed with Ollama
  -> retrieve top matching chunks
  -> send context and question to ChatOllama
  -> return an answer grounded in the retrieved wording
```

On first upload (or CLI run), Helppoa creates a Chroma vector database from the document. The web UI uses replace-the-corpus semantics — each new upload wipes and rebuilds the index. Refreshing the browser resets the session, so each visit starts with a clean state.


## 📝 Updating The Knowledge Base

### Web UI

Simply upload a new file through the browser. The previous index is replaced automatically.

### CLI

Replace or edit the source document in `data/`, then remove the local vector database so it can be rebuilt:

```bash
rm -rf db/chroma_ollama
./venv/bin/python rag.py
```

## ⚡ Caching

The app uses LangChain's `InMemoryCache` for LLM calls. This cache only lasts while the Python process is running and only applies to exact repeated prompts.

It does not cache:

- user question embeddings
- Chroma retrieval results
- semantically similar questions
- results across separate runs

## 🔎 Inspecting Chroma

Chroma stores metadata in SQLite and vector index data in binary files. To inspect the local database:

```bash
sqlite3 db/chroma_ollama/chroma.sqlite3 ".tables"
sqlite3 db/chroma_ollama/chroma.sqlite3 "select count(*) from embeddings;"
```

## ⚠️ Notes

This is a prototype, not legal advice software. The assistant is instructed to answer only from the retrieved context and preserve the source wording instead of correcting or normalizing it.
