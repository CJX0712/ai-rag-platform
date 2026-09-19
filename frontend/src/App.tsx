import { useEffect, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatPanel } from "./components/ChatPanel";
import { getHealth, uploadDocument } from "./api/client";
import type { HealthInfo } from "./api/client";

export default function App() {
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [apiKey, setApiKey] = useState<string>("");
  const [toast, setToast] = useState<string>("");

  const refreshHealth = () => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  };

  useEffect(refreshHealth, []);

  const onUpload = async (file: File) => {
    try {
      const r = await uploadDocument(file, apiKey || undefined);
      setToast(`已摄入 ${file.name}：${r.chunks} 个片段`);
      refreshHealth();
    } catch (e) {
      setToast("上传失败：" + (e as Error).message);
    }
    setTimeout(() => setToast(""), 3000);
  };

  return (
    <div className="flex h-full">
      <Sidebar
        health={health}
        apiKey={apiKey}
        onApiKey={setApiKey}
        onUpload={onUpload}
      />
      <ChatPanel apiKey={apiKey} />
      {toast && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 rounded-md border border-border bg-surface px-4 py-2 text-sm text-text">
          {toast}
        </div>
      )}
    </div>
  );
}
