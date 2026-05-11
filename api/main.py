"""FastAPI entry point for Helppoa.

Run from the project root:
    venv/bin/uvicorn api.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.rag_service import service


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


app = FastAPI(title="Helppoa API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # In dev the Vite proxy means the browser never sees the FastAPI origin
    # directly. Listed origins are a fallback if someone hits the API from a
    # different host during local hacking.
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    try:
        service.warmup()
    except Exception as exc:  # noqa: BLE001 — never block startup
        print(f"[startup] warmup skipped: {exc}")


class AskRequest(BaseModel):
    question: str


@app.get("/status")
def get_status() -> dict:
    return service.status


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{suffix}'. "
                f"Allowed: {sorted(ALLOWED_EXTENSIONS)}"
            ),
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        )

    dest = UPLOAD_DIR / file.filename
    dest.write_bytes(content)

    try:
        return service.ingest(dest)
    except Exception as exc:
        # Clean up the saved file on indexing failure so we don't leave
        # half-processed uploads on disk.
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {exc}")


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")
    try:
        return service.ask(question)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
