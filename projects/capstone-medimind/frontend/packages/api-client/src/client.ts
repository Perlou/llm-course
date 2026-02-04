/**
 * API 客户端基础配置 - 基于 Axios
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from "axios";
import type { ApiResponse } from "@medimind/types";

/** API 配置 */
export interface ApiConfig {
  baseUrl: string;
  timeout?: number;
}

/** 默认配置 */
let config: ApiConfig = {
  baseUrl: "/api/v1",
  timeout: 30000,
};

/** Axios 实例 */
let axiosInstance: AxiosInstance = createAxiosInstance();

/** 创建 Axios 实例 */
function createAxiosInstance(): AxiosInstance {
  const instance = axios.create({
    baseURL: config.baseUrl,
    timeout: config.timeout,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // 响应拦截器
  instance.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const message =
        (error.response?.data as { detail?: string })?.detail ||
        error.message ||
        "请求失败";
      return Promise.reject(new Error(message));
    },
  );

  return instance;
}

/** 配置 API 客户端 */
export function configure(options: Partial<ApiConfig>): void {
  config = { ...config, ...options };
  axiosInstance = createAxiosInstance();
}

/** 获取当前配置 */
export function getConfig(): ApiConfig {
  return config;
}

/** 获取 Axios 实例 */
export function getAxiosInstance(): AxiosInstance {
  return axiosInstance;
}

/** GET 请求 */
export async function get<T>(endpoint: string): Promise<ApiResponse<T>> {
  const response = await axiosInstance.get<ApiResponse<T>>(endpoint);
  return response.data;
}

/** POST 请求 */
export async function post<T>(
  endpoint: string,
  data?: unknown,
): Promise<ApiResponse<T>> {
  const response = await axiosInstance.post<ApiResponse<T>>(endpoint, data);
  return response.data;
}

/** DELETE 请求 */
export async function del<T>(endpoint: string): Promise<ApiResponse<T>> {
  const response = await axiosInstance.delete<ApiResponse<T>>(endpoint);
  return response.data;
}

/** 文件上传 */
export async function uploadFile<T>(
  endpoint: string,
  file: File,
): Promise<ApiResponse<T>> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axiosInstance.post<ApiResponse<T>>(
    endpoint,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );
  return response.data;
}

/** SSE 流式请求 (使用 fetch 实现，axios 不直接支持 SSE) */
export async function* streamRequest(
  endpoint: string,
  data?: unknown,
): AsyncGenerator<string, void, unknown> {
  const url = `${config.baseUrl}${endpoint}`;

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    throw new Error(`流式请求失败: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("无法读取响应流");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") return;
        yield data;
      }
    }
  }
}
