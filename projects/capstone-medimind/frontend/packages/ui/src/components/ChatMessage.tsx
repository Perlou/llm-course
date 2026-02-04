import React from "react";
import { clsx } from "clsx";
import { Bot, User } from "lucide-react";

export interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
  children?: React.ReactNode;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  timestamp,
  isStreaming = false,
  children,
}) => {
  const isUser = role === "user";

  return (
    <div
      className={clsx(
        "flex gap-3 animate-message-in",
        isUser ? "flex-row-reverse" : "flex-row",
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
          isUser
            ? "bg-gradient-to-br from-medical-blue to-sky-600 text-white"
            : "bg-gradient-to-br from-medical-green to-emerald-600 text-white",
        )}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Message Bubble */}
      <div
        className={clsx(
          "max-w-[80%] rounded-2xl px-4 py-3",
          isUser
            ? "bg-gradient-to-r from-medical-blue to-sky-600 text-white rounded-tr-sm"
            : "bg-white border border-border text-text-primary rounded-tl-sm shadow-sm",
        )}
      >
        {/* Content */}
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {content}
          {isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
          )}
        </div>

        {/* Additional content (sources, etc.) */}
        {children && <div className="mt-3">{children}</div>}

        {/* Timestamp */}
        {timestamp && (
          <div
            className={clsx(
              "text-xs mt-2",
              isUser ? "text-white/70" : "text-text-muted",
            )}
          >
            {timestamp}
          </div>
        )}
      </div>
    </div>
  );
};

ChatMessage.displayName = "ChatMessage";
