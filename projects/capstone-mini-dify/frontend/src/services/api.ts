/**
 * Mini-Dify - API 客户端
 */

import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // TODO: 添加 auth token
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || "请求失败";
    console.error("[API Error]", message);
    return Promise.reject(error);
  },
);

export default apiClient;

// ==================== Provider API ====================
export const providerApi = {
  list: () => apiClient.get("/models/providers"),
  get: (id: string) => apiClient.get(`/models/providers/${id}`),
  create: (data: any) => apiClient.post("/models/providers", data),
  update: (id: string, data: any) =>
    apiClient.put(`/models/providers/${id}`, data),
  delete: (id: string) => apiClient.delete(`/models/providers/${id}`),
  healthCheck: (id: string) => apiClient.post(`/models/providers/${id}/health`),
  chat: (data: any) => apiClient.post("/models/chat", data),
};

// ==================== Prompt API ====================
export const promptApi = {
  list: (tag?: string) => apiClient.get("/prompts", { params: { tag } }),
  get: (id: string) => apiClient.get(`/prompts/${id}`),
  create: (data: any) => apiClient.post("/prompts", data),
  update: (id: string, data: any) => apiClient.put(`/prompts/${id}`, data),
  delete: (id: string) => apiClient.delete(`/prompts/${id}`),
  versions: (id: string) => apiClient.get(`/prompts/${id}/versions`),
  rollback: (id: string, version: number) =>
    apiClient.post(`/prompts/${id}/versions/${version}/rollback`),
  test: (id: string, data: any) => apiClient.post(`/prompts/${id}/test`, data),
};

// ==================== Dataset API ====================
export const datasetApi = {
  list: () => apiClient.get("/datasets"),
  get: (id: string) => apiClient.get(`/datasets/${id}`),
  create: (data: any) => apiClient.post("/datasets", data),
  update: (id: string, data: any) => apiClient.put(`/datasets/${id}`, data),
  delete: (id: string) => apiClient.delete(`/datasets/${id}`),
  listDocuments: (id: string) => apiClient.get(`/datasets/${id}/documents`),
  uploadDocument: (id: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post(`/datasets/${id}/documents/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  deleteDocument: (datasetId: string, docId: string) =>
    apiClient.delete(`/datasets/${datasetId}/documents/${docId}`),
  retrieve: (id: string, data: any) =>
    apiClient.post(`/datasets/${id}/retrieve`, data),
};

// ==================== Agent API ====================
export const agentApi = {
  list: () => apiClient.get("/agents"),
  get: (id: string) => apiClient.get(`/agents/${id}`),
  create: (data: any) => apiClient.post("/agents", data),
  update: (id: string, data: any) => apiClient.put(`/agents/${id}`, data),
  delete: (id: string) => apiClient.delete(`/agents/${id}`),
  chat: (id: string, data: any) =>
    fetch(`${apiClient.defaults.baseURL}/agents/${id}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
};

// ==================== Tool API ====================
export const toolApi = {
  list: (type?: string) =>
    apiClient.get("/tools", { params: { tool_type: type } }),
  create: (data: any) => apiClient.post("/tools", data),
  update: (id: string, data: any) => apiClient.put(`/tools/${id}`, data),
  delete: (id: string) => apiClient.delete(`/tools/${id}`),
  initBuiltins: () => apiClient.post("/tools/init-builtins"),
};

// ==================== Workflow API ====================
export const workflowApi = {
  list: () => apiClient.get("/workflows"),
  get: (id: string) => apiClient.get(`/workflows/${id}`),
  create: (data: any) => apiClient.post("/workflows", data),
  update: (id: string, data: any) => apiClient.put(`/workflows/${id}`, data),
  delete: (id: string) => apiClient.delete(`/workflows/${id}`),
  publish: (id: string) => apiClient.post(`/workflows/${id}/publish`),
  unpublish: (id: string) => apiClient.post(`/workflows/${id}/unpublish`),
  run: (id: string, data: any) =>
    fetch(`${apiClient.defaults.baseURL}/workflows/${id}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
};

// ==================== App API ====================
export const appApi = {
  list: () => apiClient.get("/apps"),
  get: (id: string) => apiClient.get(`/apps/${id}`),
  create: (data: any) => apiClient.post("/apps", data),
  update: (id: string, data: any) => apiClient.put(`/apps/${id}`, data),
  delete: (id: string) => apiClient.delete(`/apps/${id}`),
  publish: (id: string) => apiClient.post(`/apps/${id}/publish`),
  unpublish: (id: string) => apiClient.post(`/apps/${id}/unpublish`),
  createApiKey: (id: string, name?: string) =>
    apiClient.post(`/apps/${id}/api-keys`, null, { params: { name } }),
  listApiKeys: (id: string) => apiClient.get(`/apps/${id}/api-keys`),
  deleteApiKey: (appId: string, keyId: string) =>
    apiClient.delete(`/apps/${appId}/api-keys/${keyId}`),
};

// ==================== Analytics API ====================
export const analyticsApi = {
  stats: () => apiClient.get("/analytics/stats"),
  tokenTrend: (days?: number) =>
    apiClient.get("/analytics/token-trend", { params: { days: days || 7 } }),
  logs: (page?: number, pageSize?: number, role?: string) =>
    apiClient.get("/analytics/logs", {
      params: { page: page || 1, page_size: pageSize || 20, role },
    }),
};
