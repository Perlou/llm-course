import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Send, RefreshCw } from "lucide-react";
import { triageApi } from "@medimind/api-client";
import {
  SafetyBanner,
  ChatMessage,
  EmergencyAlert,
  Input,
  Button,
  Card,
  TypingIndicator,
} from "@medimind/ui";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function TriagePage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [isEmergency, setIsEmergency] = useState(false);
  const [recommendation, setRecommendation] = useState<{
    departments: string[];
    symptoms: string[];
  } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Start session on mount
  useEffect(() => {
    startSession();
  }, []);

  const startSession = async () => {
    try {
      setIsLoading(true);
      setMessages([]);
      setIsComplete(false);
      setIsEmergency(false);
      setRecommendation(null);

      const response = await triageApi.startSession();
      setSessionId(response.session_id);
      setMessages([{ role: "assistant", content: response.message }]);
    } catch (error) {
      console.error("Start session error:", error);
      setMessages([
        {
          role: "assistant",
          content: "抱歉，服务暂时不可用，请稍后再试。",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !sessionId || isLoading || isComplete) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await triageApi.chat(sessionId, userMessage);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.message },
      ]);

      setIsComplete(response.is_complete);
      setIsEmergency(response.urgency === "emergency");

      if (response.is_complete && response.recommended_departments) {
        setRecommendation({
          departments: response.recommended_departments,
          symptoms: response.symptoms || [],
        });
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，发生错误，请重试。" },
      ]);
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
        <h1 className="font-semibold text-lg">智能导诊</h1>
        <button
          onClick={startSession}
          className="ml-auto p-2 text-text-muted hover:text-medical-blue transition-colors"
          title="重新开始"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Safety Banner */}
      <div className="px-4 py-3">
        <SafetyBanner variant="info">
          智能导诊仅供参考，具体就医请以现场医生判断为准
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
        {messages.map((msg, index) => (
          <ChatMessage key={index} role={msg.role} content={msg.content} />
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

        {/* Recommendation Card */}
        {recommendation && (
          <Card className="bg-gradient-to-br from-medical-green/10 to-emerald-50 border-medical-green/30">
            <h3 className="font-semibold text-medical-green mb-3">
              🏥 导诊建议
            </h3>

            {recommendation.symptoms.length > 0 && (
              <div className="mb-3">
                <p className="text-sm text-text-secondary mb-1">识别的症状：</p>
                <div className="flex flex-wrap gap-2">
                  {recommendation.symptoms.map((symptom, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-white rounded-full text-sm border border-border"
                    >
                      {symptom}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div>
              <p className="text-sm text-text-secondary mb-1">推荐科室：</p>
              <div className="flex flex-wrap gap-2">
                {recommendation.departments.map((dept, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-medical-green text-white rounded-lg text-sm font-medium"
                  >
                    {dept}
                  </span>
                ))}
              </div>
            </div>

            <p className="text-xs text-text-muted mt-4">
              ⚕️ 请于工作时间前往对应科室挂号就诊
            </p>
          </Card>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-white p-4 pb-24 md:pb-4">
        {isComplete ? (
          <div className="flex gap-2">
            <Button onClick={startSession} className="flex-1">
              <RefreshCw className="w-4 h-4 mr-2" />
              重新开始导诊
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="请描述您的症状..."
              disabled={isLoading}
              containerClassName="flex-1"
            />
            <Button type="submit" disabled={!input.trim() || isLoading}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
