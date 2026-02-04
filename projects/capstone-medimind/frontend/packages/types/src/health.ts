/**
 * 健康问答类型定义
 */

/** 问答请求 */
export interface ChatRequest {
  query: string;
  conversation_id?: string;
}

/** 来源信息 */
export interface SourceInfo {
  title: string;
  source?: string;
  score?: number;
}

/** 问答响应数据 */
export interface ChatResponseData {
  answer: string;
  sources: SourceInfo[];
  is_emergency: boolean;
  conversation_id: string;
  disclaimer: string;
}

/** 对话消息 */
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SourceInfo[];
  is_emergency?: boolean;
  timestamp?: string;
}

/** 对话记录 */
export interface Conversation {
  id: string;
  title: string;
  last_message?: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

/** 对话历史响应 */
export interface ConversationHistory {
  conversation_id: string;
  messages: ChatMessage[];
  total: number;
}
