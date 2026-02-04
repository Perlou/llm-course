/**
 * 健康档案 API 客户端
 */

import { post, get, del } from "./client";

/** 健康档案 */
export interface HealthProfile {
  id: string;
  user_id: string;
  gender?: string;
  birth_date?: string;
  height_cm?: number;
  weight_kg?: number;
  blood_type?: string;
  allergies?: string[];
  medical_history?: string[];
  created_at: string;
  updated_at: string;
}

/** 健康记录 */
export interface HealthRecord {
  id: string;
  record_type: string;
  value: string;
  unit?: string;
  recorded_at: string;
  notes?: string;
  created_at: string;
}

/** 更新档案请求 */
export interface UpdateProfileRequest {
  gender?: string;
  birth_date?: string;
  height_cm?: number;
  weight_kg?: number;
  blood_type?: string;
  allergies?: string[];
  medical_history?: string[];
}

/** 添加记录请求 */
export interface AddRecordRequest {
  record_type: string;
  value: string;
  unit?: string;
  recorded_at: string;
  notes?: string;
}

/**
 * 获取健康档案
 */
export async function getProfile(): Promise<HealthProfile> {
  const response = await get<HealthProfile>("/profile");
  return response.data;
}

/**
 * 更新健康档案
 */
export async function updateProfile(
  data: UpdateProfileRequest,
): Promise<HealthProfile> {
  const response = await post<HealthProfile>("/profile", data);
  return response.data;
}

/**
 * 获取健康记录列表
 */
export async function getRecords(params?: {
  record_type?: string;
  limit?: number;
  offset?: number;
}): Promise<{ records: HealthRecord[]; total: number }> {
  const query = new URLSearchParams();
  if (params?.record_type) query.append("record_type", params.record_type);
  if (params?.limit) query.append("limit", String(params.limit));
  if (params?.offset) query.append("offset", String(params.offset));

  const endpoint = `/profile/records${query.toString() ? "?" + query.toString() : ""}`;
  const response = await get<{ records: HealthRecord[]; total: number }>(
    endpoint,
  );
  return response.data;
}

/**
 * 添加健康记录
 */
export async function addRecord(data: AddRecordRequest): Promise<HealthRecord> {
  const response = await post<HealthRecord>("/profile/records", data);
  return response.data;
}

/**
 * 删除健康记录
 */
export async function deleteRecord(recordId: string): Promise<void> {
  await del(`/profile/records/${recordId}`);
}
