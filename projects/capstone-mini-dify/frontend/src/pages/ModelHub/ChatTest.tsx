import { useState } from "react";
import { X, Send, Loader2 } from "lucide-react";
import { providerApi } from "../../services/api";

interface Provider {
  id: string;
  name: string;
  provider_type: string;
  models: string[];
}

interface Props {
  provider: Provider;
  onClose: () => void;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatTest({ provider, onClose }: Props) {
  const [selectedModel, setSelectedModel] = useState(provider.models[0] || "");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: "user", content: input.trim() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const chatMessages = newMessages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const result = (await providerApi.chat({
        provider_id: provider.id,
        model: selectedModel,
        messages: chatMessages,
        stream: false,
      })) as unknown as { content: string; latency_ms: number };

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.content },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ 调用失败: ${err instanceof Error ? err.message : "未知错误"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 flex flex-col"
        style={{ height: "70vh" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-slate-800">
              对话测试 · {provider.name}
            </h3>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="text-sm px-2 py-1 rounded-md border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              {provider.models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-slate-400 py-12 text-sm">
              输入消息开始对话测试
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-indigo-500 text-white rounded-br-sm"
                    : "bg-slate-100 text-slate-700 rounded-bl-sm"
                }`}
              >
                <pre className="whitespace-pre-wrap font-sans">
                  {msg.content}
                </pre>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-100 text-slate-500 px-4 py-2.5 rounded-2xl rounded-bl-sm">
                <Loader2 className="w-4 h-4 animate-spin" />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="px-5 py-3 border-t border-slate-100">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="输入消息..."
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition-colors"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="px-4 py-2.5 rounded-xl bg-indigo-500 text-white hover:bg-indigo-600 transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
