export type Status = {
  ready: boolean;
  current_document: string | null;
  chunk_count: number;
};

export type RetrievedDoc = {
  page_content: string;
  metadata: Record<string, unknown>;
};

export type AskResponse = {
  question: string;
  answer: string;
  docs: RetrievedDoc[];
};
