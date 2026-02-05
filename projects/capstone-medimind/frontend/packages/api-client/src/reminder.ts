/**
 * MediMind - 提醒 API 客户端
 *
 * 慢病管理提醒相关接口。
 */

import { get, post, put, del } from "./client";

// ============ 类型定义 ============

/** 提醒类型 */
export type ReminderType = "medication" | "measurement" | "checkup" | "other";

/** 重复类型 */
export type RepeatType = "once" | "daily" | "weekly" | "monthly";

/** 提醒 */
export interface Reminder {
  id: string;
  title: string;
  description?: string;
  reminder_type: ReminderType;
  reminder_time: string; // HH:MM
  repeat_type: RepeatType;
  days_of_week?: number[]; // 1-7
  day_of_month?: number;
  is_enabled: boolean;
  next_trigger_at?: string;
  last_triggered_at?: string;
  created_at: string;
  updated_at: string;
}

/** 创建提醒请求 */
export interface CreateReminderRequest {
  title: string;
  description?: string;
  reminder_type?: ReminderType;
  reminder_time: string;
  repeat_type?: RepeatType;
  days_of_week?: number[];
  day_of_month?: number;
  is_enabled?: boolean;
}

/** 更新提醒请求 */
export interface UpdateReminderRequest {
  title?: string;
  description?: string;
  reminder_type?: ReminderType;
  reminder_time?: string;
  repeat_type?: RepeatType;
  days_of_week?: number[];
  day_of_month?: number;
  is_enabled?: boolean;
}

/** 提醒列表响应 */
interface ReminderListResponse {
  reminders: Reminder[];
  total: number;
}

// ============ API 方法 ============

/**
 * 获取提醒列表
 */
export async function getList(
  reminderType?: ReminderType,
): Promise<Reminder[]> {
  const params = reminderType ? `?reminder_type=${reminderType}` : "";
  const response = await get<ReminderListResponse>(`/reminder${params}`);
  return response.data.reminders;
}

/**
 * 创建提醒
 */
export async function create(data: CreateReminderRequest): Promise<Reminder> {
  const response = await post<Reminder>("/reminder", data);
  return response.data;
}

/**
 * 更新提醒
 */
export async function update(
  id: string,
  data: UpdateReminderRequest,
): Promise<Reminder> {
  const response = await put<Reminder>(`/reminder/${id}`, data);
  return response.data;
}

/**
 * 删除提醒
 */
export async function remove(id: string): Promise<void> {
  await del(`/reminder/${id}`);
}

/**
 * 启用/禁用提醒
 */
export async function toggle(id: string): Promise<Reminder> {
  const response = await post<Reminder>(`/reminder/${id}/toggle`);
  return response.data;
}

// 命名空间导出
export const reminderApi = {
  getList,
  create,
  update,
  remove,
  toggle,
};
