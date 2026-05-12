import type { AskResponse, Status } from "./types";

const BASE = "/api";

async function parseError(r: Response): Promise<string> {
  try {
    const j = await r.json();
    return typeof j.detail === "string" ? j.detail : JSON.stringify(j);
  } catch {
    return r.statusText || `HTTP ${r.status}`;
  }
}

export async function getStatus(): Promise<Status> {
  const r = await fetch(`${BASE}/status`);
  if (!r.ok) throw new Error(await parseError(r));
  return r.json();
}

export async function uploadFile(file: File): Promise<Status> {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`${BASE}/upload`, { method: "POST", body: fd });
  if (!r.ok) throw new Error(await parseError(r));
  return r.json();
}

export async function resetSession(): Promise<void> {
  const r = await fetch(`${BASE}/reset`, { method: "POST" });
  if (!r.ok) throw new Error(await parseError(r));
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const r = await fetch(`${BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!r.ok) throw new Error(await parseError(r));
  return r.json();
}
