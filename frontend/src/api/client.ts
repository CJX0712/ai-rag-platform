import axios from "axios";
import type { ChatEvent, ChatMessage } from "../types";

const http = axios.create({ baseURL: "/api/v1" });

export interface IngestResult {
  doc_id: string;
  filename: string;
  chunks: number;
  chars: number;
}

export interface HealthInfo {
  status: string;
  version: string;
  embedding_provider: string;
  llm_provider: string;
  vector_store: string;
  documents: number;
}

export async function uploadDocument(file: File, apiKey?: string): Promise<IngestResult> {
  const form = new FormData();
  form.append("file", file);
  const headers: Record<string, string> = {};
  if (apiKey) headers["Authorization"] = `Bearer ${apiKey}`;
  const { data } = await http.post<IngestResult>("/documents", form, { headers });
  return data;
}

export async function getHealth(): Promise<HealthInfo> {
  const { data } = await http.get<HealthInfo>("/health");
  return data;
}

export async function* streamChat(
  question: string,
  history: ChatMessage[] = [],
  apiKey?: string
): AsyncGenerator<ChatEvent> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (apiKey) headers["Authorization"] = `Bearer ${apiKey}`;
  const res = await fetch("/api/v1/chat", {
    method: "POST",
    headers,
    body: JSON.stringify({ question, history }),
  });
  if (!res.ok || !res.body) {
    throw new Error(`chat request failed: ${res.status}`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf("\n\n")) >= 0) {
      const frame = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      const dataLine = frame.split("\n").find((l) => l.startsWith("data: "));
      if (!dataLine) continue;
      const json = dataLine.slice(6).trim();
      if (!json) continue;
      try {
        yield JSON.parse(json) as ChatEvent;
      } catch {
        // ignore malformed frame
      }
    }
  }
}
