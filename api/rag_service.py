"""HTTP-friendly wrapper around the RAG pipeline.

The CLI in rag.py drives an interactive loop; this service exposes the same
underlying functions to a long-running process (FastAPI). Each ingest()
wipes the existing vector DB and rebuilds it from the uploaded file
(replace-the-corpus semantics).
"""

import shutil
from pathlib import Path
from threading import Lock
from typing import Any

from langchain_chroma import Chroma

from rag import (
    DB_PATH,
    build_rag_chain,
    get_embeddings,
    load_document,
    split_documents,
)


class RAGService:
    """In-process state holder for the current vectorstore and chain.

    The Lock prevents two concurrent uploads from racing on the DB directory.
    Reads (ask) do not lock because LangChain chains are thread-safe in
    the read path.
    """

    def __init__(self) -> None:
        self._chain: Any = None
        self._vectorstore: Chroma | None = None
        self._lock = Lock()
        self._current_doc: str | None = None
        self._chunk_count: int = 0

    @property
    def status(self) -> dict[str, Any]:
        return {
            "ready": self._chain is not None,
            "current_document": self._current_doc,
            "chunk_count": self._chunk_count,
        }

    def warmup(self) -> None:
        """Load an existing on-disk DB without re-embedding, if one exists."""
        db_path = Path(DB_PATH)
        if not (db_path.exists() and any(db_path.iterdir())):
            return
        vectorstore = Chroma(
            persist_directory=str(db_path),
            embedding_function=get_embeddings(),
        )
        self._vectorstore = vectorstore
        self._chain = build_rag_chain(vectorstore)
        self._current_doc = "(existing index)"
        # We don't know the chunk count from a pre-existing DB without a
        # full collection scan; report 0 and let it correct on next upload.
        self._chunk_count = 0

    def ingest(self, file_path: Path) -> dict[str, Any]:
        """Replace the corpus with file_path and rebuild the chain."""
        with self._lock:
            # Wipe the existing data BEFORE creating a new vectorstore. We
            # cannot rmtree the DB directory while a chromadb client still
            # holds a SQLite handle — that triggers SQLITE_READONLY_DBMOVED
            # (code 1032). delete_collection() drops the data through the
            # live client, keeping the SQLite file consistent for the next
            # write.
            if self._vectorstore is not None:
                try:
                    self._vectorstore.delete_collection()
                except Exception as exc:  # noqa: BLE001
                    print(f"[ingest] delete_collection failed: {exc}")
                self._vectorstore = None
                self._chain = None
            elif Path(DB_PATH).exists():
                # No live connection but a stale DB on disk (e.g. cold
                # start where warmup found nothing usable) — safe to rmtree.
                shutil.rmtree(DB_PATH)

            docs = load_document(file_path)
            chunks = split_documents(docs)
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=get_embeddings(),
                persist_directory=str(DB_PATH),
            )
            self._vectorstore = vectorstore
            self._chain = build_rag_chain(vectorstore)
            self._current_doc = file_path.name
            self._chunk_count = len(chunks)
            return self.status

    def reset(self) -> None:
        """Clear in-memory session state (chain, doc name, chunk count).
        The vectorstore reference is intentionally kept so the next ingest()
        can wipe data via delete_collection() through the same live SQLite
        connection — rmtree on an open handle causes SQLITE_READONLY_DBMOVED.
        The on-disk DB is NOT deleted here; it is overwritten on next ingest."""
        with self._lock:
            self._chain = None
            self._current_doc = None
            self._chunk_count = 0

    def ask(self, question: str) -> dict[str, Any]:
        # Snapshot avoids a race where reset() sets _chain=None between the
        # None-check and invoke().
        chain = self._chain
        if chain is None:
            raise RuntimeError("No document indexed yet. Upload a file first.")
        result = chain.invoke(question)
        return {
            "question": question,
            "answer": result["answer"],
            "docs": [
                {"page_content": d.page_content, "metadata": d.metadata}
                for d in result["docs"]
            ],
        }


service = RAGService()
