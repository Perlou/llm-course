import { useState } from "react";
import { X, Play, CheckCircle, XCircle, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { workflowApi } from "../../services/api";

interface RunResultPanelProps {
  workflowId: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onNodeStatus: (status: Record<string, any>) => void;
  onClose: () => void;
}

interface NodeEvent {
  node_id?: string;
  status?: string;
  type?: string;
  output?: string;
  error?: string;
  duration_ms?: number;
  branch?: string;
  final_output?: string;
}

export default function RunResultPanel({
  workflowId,
  onNodeStatus,
  onClose,
}: RunResultPanelProps) {
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [events, setEvents] = useState<NodeEvent[]>([]);
  const [running, setRunning] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const handleRun = async () => {
    setRunning(true);
    setEvents([]);

    const nodeStatus: Record<string, any> = {};
    onNodeStatus(nodeStatus);

    try {
      const response = await workflowApi.run(workflowId, {
        inputs: inputs,
      });

      if (!response.ok) {
        const err = await response.text();
        setEvents([{ type: "error", error: err }]);
        setRunning(false);
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        setRunning(false);
        return;
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const event: NodeEvent = JSON.parse(line.slice(6));
              setEvents((prev) => [...prev, event]);

              // Update node status
              if (event.node_id) {
                nodeStatus[event.node_id] = {
                  status: event.status,
                  output: event.output,
                  error: event.error,
                };
                onNodeStatus({ ...nodeStatus });
              }
            } catch {
              /* parse error */
            }
          }
        }
      }
    } catch (err) {
      setEvents((prev) => [
        ...prev,
        { type: "error", error: String(err) },
      ]);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="bg-white border-t border-slate-200 flex flex-col" style={{ maxHeight: expanded ? "50vh" : "48px" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-100 bg-slate-50">
        <div className="flex items-center gap-2">
          <button onClick={() => setExpanded(!expanded)} className="p-0.5">
            {expanded ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronUp className="w-4 h-4 text-slate-500" />}
          </button>
          <span className="text-sm font-medium text-slate-700">运行面板</span>
          {running && <Loader2 className="w-4 h-4 text-indigo-500 animate-spin" />}
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-200 rounded transition-colors"
        >
          <X className="w-4 h-4 text-slate-400" />
        </button>
      </div>

      {expanded && (
        <div className="flex flex-1 overflow-hidden">
          {/* Left: Inputs */}
          <div className="w-64 p-3 border-r border-slate-100 overflow-y-auto">
            <div className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wide">
              输入变量
            </div>
            <div className="space-y-2">
              <div>
                <label className="block text-xs text-slate-500 mb-0.5">
                  user_message
                </label>
                <input
                  type="text"
                  value={inputs.user_message || ""}
                  onChange={(e) =>
                    setInputs({ ...inputs, user_message: e.target.value })
                  }
                  className="w-full px-2 py-1 text-sm border border-slate-300 rounded focus:ring-1 focus:ring-indigo-500 outline-none"
                  placeholder="输入测试内容"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-500 mb-0.5">
                  自定义变量名
                </label>
                <div className="flex gap-1">
                  <input
                    type="text"
                    id="custom-var-name"
                    className="flex-1 px-2 py-1 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-indigo-500 outline-none"
                    placeholder="变量名"
                  />
                  <input
                    type="text"
                    id="custom-var-value"
                    className="flex-1 px-2 py-1 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-indigo-500 outline-none"
                    placeholder="值"
                  />
                  <button
                    onClick={() => {
                      const nameEl = document.getElementById("custom-var-name") as HTMLInputElement;
                      const valEl = document.getElementById("custom-var-value") as HTMLInputElement;
                      if (nameEl?.value && valEl?.value) {
                        setInputs({ ...inputs, [nameEl.value]: valEl.value });
                        nameEl.value = "";
                        valEl.value = "";
                      }
                    }}
                    className="px-2 py-1 text-xs bg-slate-100 rounded hover:bg-slate-200"
                  >
                    +
                  </button>
                </div>
              </div>
              {Object.entries(inputs)
                .filter(([k]) => k !== "user_message")
                .map(([key, val]) => (
                  <div key={key} className="flex items-center justify-between text-xs">
                    <span className="text-slate-600 font-mono">{key}: {val}</span>
                    <button
                      onClick={() => {
                        const newInputs = { ...inputs };
                        delete newInputs[key];
                        setInputs(newInputs);
                      }}
                      className="text-red-400 hover:text-red-500"
                    >
                      ×
                    </button>
                  </div>
                ))}
            </div>
            <button
              onClick={handleRun}
              disabled={running}
              className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors text-sm disabled:opacity-50"
            >
              {running ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  执行中...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  执行工作流
                </>
              )}
            </button>
          </div>

          {/* Right: Event Log */}
          <div className="flex-1 p-3 overflow-y-auto">
            <div className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wide">
              执行日志
            </div>
            {events.length === 0 ? (
              <div className="text-xs text-slate-400 text-center py-8">
                点击"执行工作流"开始运行
              </div>
            ) : (
              <div className="space-y-1.5">
                {events.map((evt, i) => (
                  <EventItem key={i} event={evt} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ==================== Event Item ====================

function EventItem({ event }: { event: NodeEvent }) {
  if (event.type === "workflow_completed") {
    return (
      <div className="flex items-start gap-2 p-2 bg-emerald-50 rounded-md border border-emerald-200">
        <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
        <div>
          <div className="text-xs font-medium text-emerald-700">
            工作流执行完成
          </div>
          {event.final_output && (
            <div className="text-xs text-emerald-600 mt-1 font-mono whitespace-pre-wrap">
              {event.final_output}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (event.type === "workflow_error" || event.type === "error") {
    return (
      <div className="flex items-start gap-2 p-2 bg-red-50 rounded-md border border-red-200">
        <XCircle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
        <div className="text-xs text-red-600 font-mono">{event.error}</div>
      </div>
    );
  }

  const isRunning = event.status === "running";
  const isCompleted = event.status === "completed";
  const isFailed = event.status === "failed";

  return (
    <div
      className={`flex items-start gap-2 p-2 rounded-md border text-xs ${
        isRunning
          ? "bg-blue-50 border-blue-200"
          : isCompleted
            ? "bg-slate-50 border-slate-200"
            : isFailed
              ? "bg-red-50 border-red-200"
              : "bg-slate-50 border-slate-200"
      }`}
    >
      <div className="shrink-0 mt-0.5">
        {isRunning && (
          <Loader2 className="w-3.5 h-3.5 text-blue-500 animate-spin" />
        )}
        {isCompleted && (
          <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
        )}
        {isFailed && <XCircle className="w-3.5 h-3.5 text-red-500" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-mono text-slate-700">{event.node_id}</span>
          <span className="text-slate-400">({event.type})</span>
          {event.duration_ms !== undefined && (
            <span className="text-slate-400">{event.duration_ms}ms</span>
          )}
        </div>
        {event.output && isCompleted && (
          <div className="text-slate-600 mt-1 font-mono whitespace-pre-wrap line-clamp-3">
            {event.output}
          </div>
        )}
        {event.error && (
          <div className="text-red-500 mt-1 font-mono">{event.error}</div>
        )}
        {event.branch && (
          <div className="text-amber-600 mt-1">→ 分支: {event.branch}</div>
        )}
      </div>
    </div>
  );
}
