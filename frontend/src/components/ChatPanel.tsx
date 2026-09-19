import { useEffect, useRef, useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { useChat } from "../hooks/useChat";

interface Props {
  apiKey: string;
}

export function ChatPanel({ apiKey }: Props) {
  const { messages, sources, loading, send } = useChat(apiKey || undefined);
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const submit = () => {
    if (!input.trim()) return;
    send(input);
    setInput("");
  };

  return (
    <main className="flex flex-1 flex-col">
      <header className="flex items-center gap-2 border-b border-border bg-surface px-5 py-3">
        <Sparkles size={18} className="text-accent" />
        <span className="text-sm font-medium text-text">知识问答</span>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto p-5">
        {messages.length === 0 && (
          <div className="mt-20 text-center text-sm text-muted">
            上传文档后，在此提问。系统会检索相关知识并生成回答。
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={m.role === "user" ? "flex justify-end" : "flex justify-start"}
          >
            <div
              className={
                "max-w-[80%] whitespace-pre-wrap rounded-lg px-4 py-2 text-sm " +
                (m.role === "user"
                  ? "bg-primary text-primary-fg"
                  : "border border-border bg-surface text-text")
              }
            >
              {m.content || (loading ? "思考中…" : "")}
            </div>
          </div>
        ))}
        {sources.length > 0 && (
          <div className="rounded-lg border border-border bg-surface p-3 text-xs">
            <div className="mb-1 text-muted">引用来源（{sources.length}）</div>
            {sources.map((s, i) => (
              <div key={i} className="py-1">
                <span className="text-accent">{s.source}</span>
                <span className="text-muted"> · 相关度 {s.score.toFixed(3)}</span>
                <div className="truncate text-muted">{s.snippet}</div>
              </div>
            ))}
          </div>
        )}
        <div ref={endRef} />
      </div>

      <footer className="border-t border-border bg-surface p-4">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            rows={2}
            placeholder="输入问题，Enter 发送，Shift+Enter 换行"
            className="flex-1 resize-none rounded-md border border-border bg-bg px-3 py-2 text-sm text-text outline-none focus:border-primary"
          />
          <button
            onClick={submit}
            disabled={loading}
            className="flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-fg disabled:opacity-50"
          >
            <Send size={16} /> 发送
          </button>
        </div>
      </footer>
    </main>
  );
}
