/**
 * 健康问答 API
 */

import type {
  ChatRequest,
  ChatResponseData,
  ConversationHistory,
  Conversation,
} from "@medimind/types";
import { get, post, del, streamRequest } from "./client";

/** 健康问答 API */
export const healthApi = {
  /**
   * 发送健康问题
   */
  async chat(request: ChatRequest) {
    const response = await post<ChatResponseData>("/health/chat", request);
    return response.data;
  },

  /**
   * 流式健康问答
   */
  async *chatStream(request: ChatRequest) {
    for await (const chunk of streamRequest("/health/chat/stream", request)) {
      yield chunk;
    }
  },

  /**
   * 获取对话历史
   */
  async getHistory(conversationId: string) {
    const response = await get<ConversationHistory>(
      `/health/history/${conversationId}`,
    );
    return response.data;
  },

  /**
   * 获取最近对话列表
   */
  async listConversations(limit = 20) {
    const response = await get<{
      conversations: Conversation[];
      total: number;
    }>(`/health/conversations?limit=${limit}`);
    return response.data;
  },

  /**
   * 删除对话
   */
  async deleteConversation(conversationId: string) {
    const response = await del<{ deleted: string }>(
      `/health/conversation/${conversationId}`,
    );
    return response.data;
  },
};
