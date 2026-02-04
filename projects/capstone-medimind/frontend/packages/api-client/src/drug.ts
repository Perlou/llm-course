/**
 * 药品查询 API
 */

import type {
  DrugInfo,
  DrugSearchResponse,
  DrugListResponse,
  InteractionCheckResponse,
} from "@medimind/types";
import { get, post } from "./client";

/** 药品查询 API */
export const drugApi = {
  /**
   * 搜索药品
   */
  async search(query: string, limit = 10) {
    const response = await get<DrugSearchResponse>(
      `/drug/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    );
    return response.data;
  },

  /**
   * 获取药品列表
   */
  async list(limit = 20, offset = 0) {
    const response = await get<DrugListResponse>(
      `/drug/list?limit=${limit}&offset=${offset}`,
    );
    return response.data;
  },

  /**
   * 获取药品详情
   */
  async getDetail(drugId: string) {
    const response = await get<DrugInfo>(`/drug/${drugId}`);
    return response.data;
  },

  /**
   * 检查药物相互作用
   */
  async checkInteraction(drugNames: string[]) {
    const response = await post<InteractionCheckResponse>(
      "/drug/interaction",
      drugNames,
    );
    return response.data;
  },
};
