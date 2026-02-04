import React from "react";

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <span
        className="w-2 h-2 bg-text-muted rounded-full animate-typing"
        style={{ animationDelay: "0ms" }}
      />
      <span
        className="w-2 h-2 bg-text-muted rounded-full animate-typing"
        style={{ animationDelay: "200ms" }}
      />
      <span
        className="w-2 h-2 bg-text-muted rounded-full animate-typing"
        style={{ animationDelay: "400ms" }}
      />
    </div>
  );
};

TypingIndicator.displayName = "TypingIndicator";
