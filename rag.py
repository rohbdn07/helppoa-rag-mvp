"""Local RAG pipeline for the Helppoa tenant-rights assistant."""

import os
from pathlib import Path
from typing import Iterable

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.caches import InMemoryCache
from langchain_core.documents import Document
from langchain_core.globals import set_llm_cache
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama, OllamaEmbeddings

DOCUMENT_PATH = Path(os.getenv("DOCUMENT_PATH", "data/finnish_tenant_rights.txt"))
DB_PATH = os.getenv("DB_PATH", "db/chroma_ollama")
MODEL = os.getenv("OLLAMA_MODEL", "mistral")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", MODEL)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_K = 3

set_llm_cache(InMemoryCache())

def load_document(path: Path) -> list[Document]:
    """Load a text or PDF document into LangChain Document objects."""
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    print(f"\nLoading document: {path}")
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(path))
    elif suffix in {".txt", ".md"}:
        loader = TextLoader(str(path), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported document type: {suffix}")

    docs = loader.load()
    print(f"Loaded {len(docs)} document(s)")
    return docs

def split_documents(docs: Iterable[Document]) -> list[Document]:
    """Split source documents into overlapping chunks for retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(list(docs))

    if not chunks:
        raise ValueError("No text chunks were created from the source document.")
    
    print(f"Created {len(chunks)} chunks")
    return chunks

def get_embeddings() -> OllamaEmbeddings:
    """Create the embeeding model used by Chroma."""
    return OllamaEmbeddings(model=EMBED_MODEL)

def create_vectorstore(chunks: list[Document]) -> Chroma:
    """Embed document chunks and persist them in Chroma."""
    print(f"Creating vector store at {DB_PATH}")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=DB_PATH,
    )
    print(f"Stored {len(chunks)} chunks")
    return vectorstore

def load_vectorstore() -> Chroma:
    """Load an existing Chroma vector store"""
    print(f"Loading vector store from {DB_PATH}")
    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=get_embeddings()
    )


if __name__ == "__main__":
    main()
