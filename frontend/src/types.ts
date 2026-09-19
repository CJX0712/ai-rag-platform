export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface SourceRef {
  source: string;
  score: number;
  snippet: string;
}

export type ChatEvent =
  | { type: "sources"; sources: SourceRef[] }
  | { type: "token"; text: string }
  | { type: "done"; session_id: string }
  | { type: "end" };
