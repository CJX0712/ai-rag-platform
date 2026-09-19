import { useCallback, useState } from "react";
import type { ChatMessage, SourceRef } from "../types";
import { streamChat } from "../api/client";

export function useChat(apiKey?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sources, setSources] = useState<SourceRef[]>([]);
  const [loading, setLoading] = useState(false);

  const send = useCallback(
    async (question: string) => {
      if (!question.trim() || loading) return;
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      setMessages((prev) => [
        ...prev,
        { role: "user", content: question },
        { role: "assistant", content: "" },
      ]);
      setLoading(true);
      setSources([]);
      let acc = "";
      try {
        const stream = streamChat(question, history, apiKey);
        for await (const ev of stream) {
          if (ev.type === "sources") {
            setSources(ev.sources);
          } else if (ev.type === "token") {
            acc += ev.text;
            setMessages((prev) => {
              const copy = [...prev];
              copy[copy.length - 1] = { role: "assistant", content: acc };
              return copy;
            });
          }
        }
      } catch (e) {
        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = {
            role: "assistant",
            content: "请求失败：" + (e as Error).message,
          };
          return copy;
        });
      } finally {
        setLoading(false);
      }
    },
    [messages, loading, apiKey]
  );

  return { messages, sources, loading, send };
}
