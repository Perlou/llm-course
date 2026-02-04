/**
 * 智能导诊类型定义
 */

/** 导诊状态 */
export type TriageState =
  | "greeting"
  | "collecting"
  | "analyzing"
  | "recommending"
  | "complete";

/** 紧急程度 */
export type UrgencyLevel = "normal" | "attention" | "urgent" | "emergency";

/** 开始会话响应 */
export interface StartSessionResponse {
  session_id: string;
  state: TriageState;
  message: string;
}

/** 对话请求 */
export interface TriageChatRequest {
  message: string;
}

/** 对话响应 */
export interface TriageChatResponse {
  session_id: string;
  state: TriageState;
  urgency: UrgencyLevel;
  message: string;
  is_complete: boolean;
  recommended_departments?: string[];
  symptoms?: string[];
}

/** 会话状态响应 */
export interface SessionStatusResponse {
  session_id: string;
  state: TriageState;
  urgency: UrgencyLevel;
  symptoms: string[];
  recommended_departments: string[];
  questions_asked: number;
  is_complete: boolean;
}

/** 会话历史响应 */
export interface SessionHistoryResponse {
  session_id: string;
  messages: {
    role: "user" | "assistant";
    content: string;
  }[];
  total: number;
}

/** 科室信息 */
export interface Department {
  id: string;
  name: string;
  description: string;
}
