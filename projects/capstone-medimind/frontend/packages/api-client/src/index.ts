/**
 * @medimind/api-client - MediMind API 客户端
 */

// 客户端配置
export { configure, getConfig } from "./client";
export type { ApiConfig } from "./client";

// API 模块
export { healthApi } from "./health";
export { drugApi } from "./drug";
export { reportApi } from "./report";
export { triageApi } from "./triage";

// 重新导出类型
export type * from "@medimind/types";
