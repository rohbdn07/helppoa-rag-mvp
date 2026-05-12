import { useEffect, useState } from "react";
import { FileUpload } from "./components/FileUpload";
import { ChatBox } from "./components/ChatBox";
import { getStatus, resetSession } from "./api";
import type { Status } from "./types";

export default function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      setStatus(await getStatus());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  useEffect(() => {
    resetSession().catch(() => null).then(refresh);
  }, []);

  return (
    <div className="container">
      <header>
        <h1>Helppoa</h1>
        <p className="subtitle">
          Local RAG Q&A — upload a document, then ask questions grounded in it.
        </p>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="card">
        <h2>1. Upload a document</h2>
        <FileUpload onUploaded={refresh} />
        {status && (
          <div className="status">
            {status.ready ? (
              <>
                Indexed{" "}
                <code>{status.current_document ?? "(unknown)"}</code>
                {status.chunk_count > 0 && (
                  <> — {status.chunk_count} chunks</>
                )}
              </>
            ) : (
              <>No document indexed yet. Upload a PDF or text file to get started.</>
            )}
          </div>
        )}
      </section>

      <section className="card">
        <h2>2. Ask a question</h2>
        <ChatBox disabled={!status?.ready} />
      </section>
    </div>
  );
}
