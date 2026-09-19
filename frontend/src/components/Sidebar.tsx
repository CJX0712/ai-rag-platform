import type { ReactNode } from "react";
import { Cpu, Database, FileText, KeyRound, Upload } from "lucide-react";
import type { HealthInfo } from "../api/client";

interface Props {
  health: HealthInfo | null;
  apiKey: string;
  onApiKey: (v: string) => void;
  onUpload: (f: File) => void;
}

export function Sidebar({ health, apiKey, onApiKey, onUpload }: Props) {
  return (
    <aside className="flex w-72 flex-col gap-4 border-r border-border bg-surface p-4">
      <div className="flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-fg">
          <Database size={18} />
        </div>
        <div>
          <div className="text-sm font-semibold text-text">AI RAG 平台</div>
          <div className="text-xs text-muted">检索增强问答</div>
        </div>
      </div>

      <label className="flex cursor-pointer items-center justify-center gap-2 rounded-md border border-border bg-bg px-3 py-2 text-sm text-text hover:border-primary">
        <Upload size={16} />
        上传知识文档
        <input
          type="file"
          className="hidden"
          accept=".pdf,.txt,.md,.html"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onUpload(f);
            e.target.value = "";
          }}
        />
      </label>

      <div className="rounded-md border border-border bg-bg p-3 text-xs text-muted">
        <div className="mb-2 flex items-center gap-2 text-text">
          <Cpu size={14} /> 运行状态
        </div>
        <Row icon={<Database size={13} />} label="向量库" value={health?.vector_store ?? "-"} />
        <Row icon={<Cpu size={13} />} label="嵌入服务" value={health?.embedding_provider ?? "-"} />
        <Row icon={<FileText size={13} />} label="生成模型" value={health?.llm_provider ?? "-"} />
        <Row icon={<Database size={13} />} label="已存文档" value={String(health?.documents ?? 0)} />
      </div>

      <div className="mt-auto">
        <label className="mb-1 flex items-center gap-2 text-xs text-muted">
          <KeyRound size={13} /> API Key（可选）
        </label>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => onApiKey(e.target.value)}
          placeholder="未设置则接口开放"
          className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text outline-none focus:border-primary"
        />
      </div>
    </aside>
  );
}

function Row({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="flex items-center gap-1.5">
        {icon}
        {label}
      </span>
      <span className="text-text">{value}</span>
    </div>
  );
}
