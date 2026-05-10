# Helppoa

Helppoa is a local retrieval-augmented generation (RAG) prototype for answering questions from a small tenant-rights knowledge base. The project runs locally with Ollama, Mistral, LangChain, and ChromaDB.

## Features

- Local document ingestion for `.txt`, `.md`, and `.pdf` files
- Chunking with overlap for better retrieval context
- Local embeddings through Ollama
- Persistent local vector storage with ChromaDB
- Extractive local chat responses through `ChatOllama`
- In-memory LLM response cache for repeated identical prompts
- Interactive CLI mode for questions

## Requirements

- Python 3.11 or newer
- Ollama installed and running
- The `mistral` Ollama model

Install the Ollama model:

```bash
ollama pull mistral
```

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the app:

```bash
./venv/bin/python rag.py
```

## Configuration

The app works with defaults, but these environment variables can override them:

```bash
export DOCUMENT_PATH="data/finnish_tenant_rights.txt"
export DB_PATH="db/chroma_ollama"
export OLLAMA_MODEL="mistral"
export OLLAMA_EMBED_MODEL="mistral"
```

## Project Structure

```text
helppoa/
├── data/
│   └── finnish_tenant_rights.txt
├── rag.py
├── requirements.txt
└── README.md
```

`db/chroma_ollama/` is created locally on first run and is ignored by Git.

## How It Works

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

On the first run, Helppoa creates a Chroma vector database from the configured document. On later runs, it loads the existing vector database to avoid re-embedding the same source text.

## Updating The Knowledge Base

Replace or edit the source document in `data/`, then remove the local vector database so it can be rebuilt:

```bash
rm -rf db/chroma_ollama
./venv/bin/python rag.py
```

## Caching

The app uses LangChain's `InMemoryCache` for LLM calls. This cache only lasts while the Python process is running and only applies to exact repeated prompts.

It does not cache:

- user question embeddings
- Chroma retrieval results
- semantically similar questions
- results across separate runs

## Inspecting Chroma

Chroma stores metadata in SQLite and vector index data in binary files. To inspect the local database:

```bash
sqlite3 db/chroma_ollama/chroma.sqlite3 ".tables"
sqlite3 db/chroma_ollama/chroma.sqlite3 "select count(*) from embeddings;"
```

## Notes

This is a prototype, not legal advice software. The assistant is instructed to answer only from the retrieved context and preserve the source wording instead of correcting or normalizing it.
