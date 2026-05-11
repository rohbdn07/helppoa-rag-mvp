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
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ─── CONFIG ──────────────────────────────────────────────────
DOCUMENT_PATH    = Path(os.getenv("DOCUMENT_PATH", "data/helppoa_test_reference.pdf"))
DB_PATH          = os.getenv("DB_PATH", "db/chroma_ollama")
MODEL            = os.getenv("OLLAMA_MODEL", "mistral")
EMBED_MODEL      = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHUNK_SIZE       = 1000
CHUNK_OVERLAP    = 150
RETRIEVAL_K      = 5

# Cache same questions — no repeated LLM calls
set_llm_cache(InMemoryCache())


# ─── STEP 1: LOAD DOCUMENT ───────────────────────────────────
def load_document(path: Path) -> list[Document]:
    """Load .txt or .pdf file into LangChain Document objects."""
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    print(f"\n📄 Loading document: {path}")
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(path))
    elif suffix in {".txt", ".md"}:
        loader = TextLoader(str(path), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported document type: {suffix}")

    docs = loader.load()
    print(f"   Loaded {len(docs)} document(s)")
    return docs


# ─── STEP 2: SPLIT INTO CHUNKS ───────────────────────────────
def split_documents(docs: Iterable[Document]) -> list[Document]:
    """
    Split documents into overlapping chunks, preferring section boundaries.

    Separators are tried in order; the splitter only falls through to the next
    one when a piece is still larger than chunk_size. ". " (with space) avoids
    splitting on decimals like "§ 5.2" or abbreviations like "e.g.".
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(list(docs))

    if not chunks:
        raise ValueError("No chunks created from document.")

    print(f"   Created {len(chunks)} chunks")
    print(f"\n   Example chunk:\n   {'─'*40}")
    print(f"   {chunks[0].page_content[:200]}...")
    print(f"   {'─'*40}")
    return chunks


# ─── STEP 3: EMBEDDINGS ──────────────────────────────────────
def get_embeddings() -> OllamaEmbeddings:
    """Local Ollama embeddings — free, no API needed."""
    return OllamaEmbeddings(model=EMBED_MODEL)


# ─── STEP 4: VECTOR STORE ────────────────────────────────────
def create_vectorstore(chunks: list[Document]) -> Chroma:
    """Embed chunks and store in ChromaDB."""
    print(f"\n🧮 Creating embeddings → ChromaDB at {DB_PATH}")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=DB_PATH,
    )
    print(f"   Stored {len(chunks)} chunks ✅")
    return vectorstore


def load_vectorstore() -> Chroma:
    """Load existing ChromaDB — skip re-embedding."""
    print(f"\n📦 Loading existing ChromaDB from {DB_PATH}")
    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=get_embeddings(),
    )


def get_vectorstore() -> Chroma:
    """Load existing DB if present, otherwise build it from the source document.

    To force a rebuild (e.g. after editing the document, swapping the embedder,
    or changing chunking config), delete the DB directory:
        rm -rf db/chroma_ollama
    """
    db_path = Path(DB_PATH)
    if db_path.exists() and any(db_path.iterdir()):
        return load_vectorstore()

    docs   = load_document(DOCUMENT_PATH)
    chunks = split_documents(docs)
    return create_vectorstore(chunks)


# ─── STEP 5: BUILD RAG CHAIN ─────────────────────────────────
def build_rag_chain(vectorstore: Chroma):
    prompt_template = """You are Helppoa, a calm assistant that helps people navigate
legal and civic situations in Finland.

Answer ONLY from the Context below. The Context is drawn from official Finnish
sources — treat it as authoritative for this question. Do not add information
from outside the Context, and do not "correct" it using general knowledge.

Rules:
- Quote the relevant phrase from the Context verbatim, in quotes, then briefly
  explain it in plain language.
- If the Context is ambiguous or only partially answers the question, say so
  explicitly rather than guessing.
- If the answer is not in the Context, reply with EXACTLY:
  "I don't have this information in my database."
- Do not recommend external websites, lawyers, or services unless the Context
  names them.
- Keep the answer to 1–3 sentences.

Context:
{context}

Question: {question}

Answer:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )

    llm = ChatOllama(
        model=MODEL,
        temperature=0.0,
    )

    # Pure ChromaDB semantic search — no re-ranking
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVAL_K},
    )

    def format_docs(docs: list[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    # Retrieve once, then fan out to the LLM while keeping the raw docs.
    # Final shape: {"docs": [...], "question": "...", "answer": "..."}
    chain = (
        RunnableParallel(
            docs=retriever,
            question=RunnablePassthrough(),
        )
        | RunnablePassthrough.assign(
            answer=(
                {
                    "context": lambda x: format_docs(x["docs"]),
                    "question": lambda x: x["question"],
                }
                | prompt
                | llm
                | StrOutputParser()
            )
        )
    )

    return chain


# ─── STEP 6: ASK ─────────────────────────────────────────────
def ask(chain, question: str) -> None:
    """Run query through RAG pipeline and print answer + retrieved chunks."""
    print(f"\n{'='*60}")
    print(f"❓ Question: {question}")
    print(f"{'='*60}")

    result = chain.invoke(question)
    answer = result["answer"]
    docs = result["docs"]

    print(f"\n💬 Helppoa says:\n\n   {answer}")
    print(f"\n📎 Retrieved chunks ({len(docs)}):")
    for i, doc in enumerate(docs, 1):
        snippet = " ".join(doc.page_content.split())[:120]
        source  = doc.metadata.get("source", "unknown")
        page    = doc.metadata.get("page")
        loc     = f"{source}, page {page + 1}" if page is not None else source
        print(f"   [{i}] {loc}: {snippet}...")


# ─── MAIN ────────────────────────────────────────────────────
def main() -> None:
    print("🌍 HELPPOA — Local RAG")
    print("=" * 60)
    print(f"   Document  : {DOCUMENT_PATH}")
    print(f"   Model     : {MODEL}")
    print(f"   Embeddings: {EMBED_MODEL}")

    vectorstore = get_vectorstore()
    chain = build_rag_chain(vectorstore)

    # Interactive mode
    print("\n" + "="*60)
    print("💬 Interactive mode — type your question (or 'quit' to exit)")
    print("="*60)

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"quit", "exit", "q", "bye"}:
            print("\nGoodbye! 👋")
            break
        if user_input:
            ask(chain, user_input)


if __name__ == "__main__":
    main()
