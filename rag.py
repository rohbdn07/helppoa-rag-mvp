"""Local RAG pipeline for the Helppoa tenant-rights assistant."""

import os
from pathlib import Path
from typing import Iterable

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.caches import InMemoryCache
from langchain_core.documents import Document
from langchain_core.globals import set_llm_cache

DOCUMENT_PATH = Path(os.getenv("DOCUMENT_PATH", "data/finnish_tenant_rights.txt"))
DB_PATH = os.getenv("DB_PATH", "db/chroma_ollama")
MODEL = os.getenv("OLLAMA_MODEL", "mistral")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", MODEL)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_K = 3

set_llm_cache(InMemoryCache())


if __name__ == "__main__":
    main()
