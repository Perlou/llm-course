import { useState, useRef, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Send, Camera, Mic, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { healthApi } from "@medimind/api-client";
import type {
  ChatMessage as ChatMessageType,
  SourceInfo,
} from "@medimind/types";
import {
  SafetyBanner,
  ChatMessage,
  SourceCard,
  EmergencyAlert,
  Input,
  Button,
  TypingIndicator,
} from "@medimind/ui";

export default function HealthQAPage() {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState(initialQuery);
  const [isLoading, setIsLoading] = useState(false);
  const [isEmergency, setIsEmergency] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle initial query
  useEffect(() => {
    if (initialQuery && messages.length === 0) {
      handleSend(initialQuery);
    }
  }, []);

  const handleSend = async (query?: string) => {
    const message = query || input.trim();
    if (!message || isLoading) return;

    // Add user message
    const userMessage: ChatMessageType = {
      role: "user",
      content: message,
      timestamp: new Date().toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Use streaming API
      let fullAnswer = "";
      const sources: SourceInfo[] = [];

      // For demo, use non-streaming API first
      const response = await healthApi.chat({
        query: message,
        conversation_id: conversationId || undefined,
      });

      fullAnswer = response.answer;
      sources.push(...response.sources);
      setConversationId(response.conversation_id);
      setIsEmergency(response.is_emergency);

      // Add AI message
      const aiMessage: ChatMessageType = {
        role: "assistant",
        content: fullAnswer,
        sources,
        is_emergency: response.is_emergency,
        timestamp: new Date().toLocaleTimeString("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: ChatMessageType = {
        role: "assistant",
        content: "抱歉，服务暂时不可用，请稍后再试。",
        timestamp: new Date().toLocaleTimeString("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <div className="flex-1 flex flex-col max-w-2xl mx-auto w-full">
      {/* Header */}
      <div className="px-4 py-3 flex items-center gap-3 border-b border-border bg-white md:hidden">
        <Link
          to="/"
          className="p-1 -ml-1 text-text-secondary hover:text-text-primary"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="font-semibold text-lg">健康问答</h1>
      </div>

      {/* Safety Banner */}
      <div className="px-4 py-3">
        <SafetyBanner variant="info">
          温馨提示：AI建议仅供参考，不能代替专业医疗诊断，紧急情况请立即就医。
        </SafetyBanner>
      </div>

      {/* Emergency Alert */}
      {isEmergency && (
        <div className="px-4 pb-3">
          <EmergencyAlert />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-text-muted py-8">
            <p>👋 您好！请输入您的健康问题</p>
            <p className="text-sm mt-2">例如：高血压应该注意什么？</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          >
            {/* Sources */}
            {msg.sources && msg.sources.length > 0 && (
              <div className="space-y-2 mt-3 border-t border-border/50 pt-3">
                <p className="text-xs text-text-muted">📖 参考来源：</p>
                {msg.sources.map((source, i) => (
                  <SourceCard
                    key={i}
                    title={source.title}
                    source={source.source}
                    score={source.score}
                  />
                ))}
              </div>
            )}
          </ChatMessage>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-medical-green to-emerald-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs">AI</span>
            </div>
            <div className="bg-white border border-border rounded-2xl rounded-tl-sm shadow-sm">
              <TypingIndicator />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-white p-4 pb-24 md:pb-4">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <button
            type="button"
            className="p-2 text-text-muted hover:text-medical-blue transition-colors"
          >
            <Camera className="w-5 h-5" />
          </button>

          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="请输入您的问题..."
            disabled={isLoading}
            containerClassName="flex-1"
          />

          <button
            type="button"
            className="p-2 text-text-muted hover:text-medical-blue transition-colors"
          >
            <Mic className="w-5 h-5" />
          </button>

          <Button type="submit" disabled={!input.trim() || isLoading}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
