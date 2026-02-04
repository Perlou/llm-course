/**
 * MediMind API 响应类型
 */

/** 统一 API 响应格式 */
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
  disclaimer?: string;
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

/** API 错误 */
export interface ApiError {
  code: number;
  message: string;
  detail?: string;
}
