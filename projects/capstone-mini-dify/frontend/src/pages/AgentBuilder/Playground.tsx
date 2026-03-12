import { useState, useRef, useEffect } from "react";
import { ArrowLeft, Send, Loader2, Bot, User, Wrench } from "lucide-react";
import { agentApi } from "../../services/api";

interface AgentItem {
  id: string;
  name: string;
  model_name: string;
  strategy: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ToolEvent {
  type: "tool_call" | "tool_result";
  data: string;
}

interface Props {
  agent: AgentItem;
  onBack: () => void;
}

export default function Playground({ agent, onBack }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [toolEvents, setToolEvents] = useState<ToolEvent[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streaming]);

  const handleSend = async () => {
    if (!input.trim() || streaming) return;
    const userMsg: Message = { role: "user", content: input.trim() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setStreaming(true);
    setToolEvents([]);

    try {
      const res = await agentApi.chat(agent.id, {
        messages: newMessages.map((m) => ({
          role: m.role,
          content: m.content,
        })),
      });

      if (!res.body) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "连接失败" },
        ]);
        setStreaming(false);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";
      let buffer = "";

      // Add placeholder assistant message
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            const eventType = line.replace("event: ", "").trim();
            // next line should be data
            const dataLineIdx = lines.indexOf(line) + 1;
            if (dataLineIdx < lines.length) {
              const dataLine = lines[dataLineIdx];
              if (dataLine.startsWith("data: ")) {
                const rawData = dataLine.replace("data: ", "");
                try {
                  const parsed = JSON.parse(rawData);
                  if (eventType === "message") {
                    assistantContent += parsed;
                    setMessages((prev) => {
                      const updated = [...prev];
                      updated[updated.length - 1] = {
                        role: "assistant",
                        content: assistantContent,
                      };
                      return updated;
                    });
                  } else if (
                    eventType === "tool_call" ||
                    eventType === "tool_result"
                  ) {
                    setToolEvents((prev) => [
                      ...prev,
                      { type: eventType as "tool_call" | "tool_result", data: parsed },
                    ]);
                  }
                } catch {
                  // skip malformed data
                }
              }
            }
          } else if (line.startsWith("data: ")) {
            // simple data-only line (without preceding event line)
            const rawData = line.replace("data: ", "");
            try {
              const parsed = JSON.parse(rawData);
              if (typeof parsed === "string") {
                assistantContent += parsed;
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    role: "assistant",
                    content: assistantContent,
                  };
                  return updated;
                });
              }
            } catch {
              // skip
            }
          }
        }
      }
    } catch (err) {
      console.error("Chat failed", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "请求失败，请检查 Agent 配置" },
      ]);
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-3 border-b border-slate-200 bg-white">
        <button
          onClick={onBack}
          className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-violet-500" />
          <h2 className="font-semibold text-slate-800">{agent.name}</h2>
        </div>
        <div className="flex items-center gap-2 ml-auto text-xs text-slate-400">
          <span className="px-2 py-0.5 rounded bg-slate-100">
            {agent.model_name}
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-100">
            {agent.strategy}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-16 text-slate-400">
            <Bot className="w-10 h-10 mx-auto mb-3 opacity-40" />
            <p className="text-sm">开始与 {agent.name} 对话</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-violet-600" />
              </div>
            )}
            <div
              className={`max-w-[70%] px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed ${
                msg.role === "user"
                  ? "bg-indigo-500 text-white rounded-br-md"
                  : "bg-slate-100 text-slate-700 rounded-bl-md"
              }`}
            >
              {msg.content || (streaming && i === messages.length - 1 ? (
                <span className="flex items-center gap-1 text-slate-400">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  思考中...
                </span>
              ) : "")}
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-indigo-600" />
              </div>
            )}
          </div>
        ))}

        {/* Tool events */}
        {toolEvents.length > 0 && (
          <div className="space-y-1.5 ml-11">
            {toolEvents.map((te, i) => (
              <div
                key={i}
                className="flex items-start gap-2 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 text-xs"
              >
                <Wrench className="w-3.5 h-3.5 text-amber-500 mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <span className="font-medium text-amber-700">
                    {te.type === "tool_call" ? "调用工具" : "工具返回"}
                  </span>
                  <pre className="mt-0.5 text-amber-600 whitespace-pre-wrap break-all">
                    {te.data}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-6 py-3 border-t border-slate-200 bg-white">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="输入消息..."
            disabled={streaming}
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={streaming || !input.trim()}
            className="p-2.5 rounded-xl bg-indigo-500 text-white hover:bg-indigo-600 disabled:opacity-50 transition-colors"
          >
            {streaming ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
