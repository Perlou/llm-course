/**
 * 认证 API 客户端
 */

import { post, get } from "./client";

/** 用户信息 */
export interface User {
  id: string;
  email: string;
  nickname?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

/** 注册请求 */
export interface RegisterRequest {
  email: string;
  password: string;
  nickname?: string;
}

/** 登录请求 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** 登录响应 */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

/** 更新用户请求 */
export interface UpdateUserRequest {
  nickname?: string;
  avatar_url?: string;
}

/**
 * 用户注册
 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await post<AuthResponse>("/auth/register", data);
  return response.data;
}

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await post<AuthResponse>("/auth/login", data);
  return response.data;
}

/**
 * 用户登出
 */
export async function logout(): Promise<void> {
  await post("/auth/logout");
}

/**
 * 获取当前用户信息
 */
export async function getMe(): Promise<User> {
  const response = await get<User>("/auth/me");
  return response.data;
}

/**
 * 更新用户信息
 */
export async function updateMe(data: UpdateUserRequest): Promise<User> {
  const response = await post<User>("/auth/me", data);
  return response.data;
}
