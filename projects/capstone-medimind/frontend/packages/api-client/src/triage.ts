/**
 * 智能导诊 API
 */

import type {
  StartSessionResponse,
  TriageChatResponse,
  SessionStatusResponse,
  SessionHistoryResponse,
  Department,
} from "@medimind/types";
import { get, post } from "./client";

/** 智能导诊 API */
export const triageApi = {
  /**
   * 开始导诊会话
   */
  async startSession() {
    const response = await post<StartSessionResponse>("/triage/start");
    return response.data;
  },

  /**
   * 发送消息
   */
  async chat(sessionId: string, message: string) {
    const response = await post<TriageChatResponse>(
      `/triage/${sessionId}/chat`,
      { message },
    );
    return response.data;
  },

  /**
   * 获取会话状态
   */
  async getStatus(sessionId: string) {
    const response = await get<SessionStatusResponse>(
      `/triage/${sessionId}/status`,
    );
    return response.data;
  },

  /**
   * 获取会话历史
   */
  async getHistory(sessionId: string) {
    const response = await get<SessionHistoryResponse>(
      `/triage/${sessionId}/history`,
    );
    return response.data;
  },

  /**
   * 结束会话
   */
  async endSession(sessionId: string) {
    const response = await post<TriageChatResponse>(`/triage/${sessionId}/end`);
    return response.data;
  },

  /**
   * 获取科室列表
   */
  async listDepartments() {
    const response = await get<{ departments: Department[]; total: number }>(
      "/triage/departments",
    );
    return response.data;
  },
};
