import { useState } from "react";
import type { FormEvent } from "react";
import { askQuestion } from "../api";
import type { AskResponse } from "../types";

type Props = { disabled: boolean };

type Turn = {
  question: string;
  answer: string;
  docs: AskResponse["docs"];
};

function chunkLocation(metadata: Record<string, unknown>): string {
  const source = String(metadata.source ?? "unknown");
  const page = metadata.page;
  if (typeof page === "number") return `${source}, page ${page + 1}`;
  return source;
}

function compactSnippet(text: string, max = 200): string {
  const collapsed = text.replace(/\s+/g, " ").trim();
  return collapsed.length > max ? `${collapsed.slice(0, max)}…` : collapsed;
}

export function ChatBox({ disabled }: Props) {
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;
    setBusy(true);
    setError(null);
    try {
      const r = await askQuestion(q);
      setTurns([{ question: r.question, answer: r.answer, docs: r.docs }, ...turns]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const placeholder = disabled
    ? "Upload a document first…"
    : "Ask a question about the document…";

  return (
    <div className="chat-box">
      <form onSubmit={submit} className="chat-form">
        <input
          type="text"
          placeholder={placeholder}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={disabled || busy}
        />
        <button
          type="submit"
          disabled={disabled || busy || question.trim().length === 0}
        >
          {busy ? "Thinking…" : "Ask"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      <div className="turns">
        {turns.map((turn, idx) => (
          <article key={turns.length - idx} className="turn">
            <div className="q">
              <span className="label">Q</span>
              <span>{turn.question}</span>
            </div>
            <div className="a">
              <span className="label">A</span>
              <span>{turn.answer}</span>
            </div>
            <details className="citations">
              <summary>{turn.docs.length} retrieved chunks</summary>
              <ol>
                {turn.docs.map((doc, i) => (
                  <li key={i}>
                    <code>{chunkLocation(doc.metadata)}</code>
                    <span className="snippet">
                      {compactSnippet(doc.page_content)}
                    </span>
                  </li>
                ))}
              </ol>
            </details>
          </article>
        ))}
      </div>
    </div>
  );
}
