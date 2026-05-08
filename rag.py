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
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

def get_vectorstore() -> Chroma:
    """Load the persisted vector store or create it from the source document."""
    db_path = Path(DB_PATH)

    if db_path.exists() and any(db_path.iterdir()):
        return load_vectorstore()

    docs = load_document(DOCUMENT_PATH)
    chunks = split_documents(docs)
    return create_vectorstore(chunks)

def build_rag_chain(vectorstore: Chroma):
    """Build the retrieval and generation chain."""
    prompt_template = """You are Helppoa, a calm and practical assistant for legal and civic questions.

Use only the context below to answer. Do not use outside knowledge.

If the answer is not in the context, respond exactly with:
"I don't have this information in my database."

When the answer is in the context:
- Be concise and reassuring.
- Include contact details only if they are present in the context.
- Suggest next steps based only on the context.

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
        temperature=0.1,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVAL_K},
    )

    def format_docs(docs: list[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever

def ask(chain_tuple, question: str) -> None:
    """Answer a question and print retrieved source snippets."""
    chain, retriever = chain_tuple

    print(f"\nQuestion: {question}")
    print("-" * 80)

    answer = chain.invoke(question)
    print(f"\nAnswer:\n{answer}")

    docs = retriever.invoke(question)
    print("\nRetrieved chunks:")
    for index, doc in enumerate(docs, 1):
        snippet = " ".join(doc.page_content.split())[:140]
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page")
        location = f"{source}, page {page + 1}" if page is not None else source
        print(f"[{index}] {location}: {snippet}...")

def main() -> None:
    print("Helppoa local RAG")
    print("=" * 80)
    print(f"Document: {DOCUMENT_PATH}")
    print(f"Model: {MODEL}")
    print(f"Embedding model: {EMBED_MODEL}")

    vectorstore = get_vectorstore()
    chain_tuple = build_rag_chain(vectorstore)

    test_questions = [
        "My landlord won't return my deposit. What should I do?",
        "The heating in my apartment is broken. Who is responsible?",
        "My landlord wants to increase my rent. Is this legal?",
        "I got illegally evicted. What can I do?",
    ]

    for question in test_questions:
        ask(chain_tuple, question)

    print("\nInteractive mode. Type 'quit' or 'bye' to exit.")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"quit", "exit", "q", "bye"}:
            print("Goodbye. Thanks for the conversation!")
            break
        if user_input:
            ask(chain_tuple, user_input)


if __name__ == "__main__":
    main()
