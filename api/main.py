"""FastAPI entry point for Helppoa.

Run from the project root:
    venv/bin/uvicorn api.main:app --reload
"""

import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.rag_service import service


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        service.warmup()
    except Exception as exc:  # noqa: BLE001 — never block startup
        print(f"[startup] warmup skipped: {exc}")
    yield


app = FastAPI(title="Helppoa API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/status")
def get_status() -> dict:
    return service.status


@app.post("/reset")
def reset_session() -> dict:
    service.reset()
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

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        dest = Path(tmp.name)

    try:
        return service.ingest(dest)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {exc}")
    finally:
        dest.unlink(missing_ok=True)


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")
    try:
        return service.ask(question)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
