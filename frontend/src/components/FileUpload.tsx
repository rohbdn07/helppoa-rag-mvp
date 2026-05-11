import { useRef, useState } from "react";
import type { ChangeEvent } from "react";
import { uploadFile } from "../api";

type Props = { onUploaded: () => void };

export function FileUpload({ onUploaded }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setBusy(true);
    setError(null);
    try {
      await uploadFile(file);
      onUploaded();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
      // Reset so the same file can be re-uploaded if needed.
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div className="file-upload">
      <label className="file-upload-label">
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleChange}
          disabled={busy}
        />
        {busy
          ? `Indexing ${fileName ?? "file"}…`
          : "Choose a PDF or text file"}
      </label>
      <div className="hint">Accepted: .pdf, .txt, .md (max 25 MB)</div>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
