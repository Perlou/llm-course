/**
 * 医院搜索 API
 */

import { get, post } from "./client";

/** 位置信息 */
export interface Location {
  lat: number;
  lng: number;
}

/** 医院信息 */
export interface Hospital {
  id: string;
  name: string;
  address: string;
  tel?: string;
  distance?: number;
  type_name?: string;
  rating?: number;
  location?: Location;
}

/** 周边搜索参数 */
export interface NearbySearchParams {
  lat: number;
  lng: number;
  keyword?: string;
  radius?: number;
  page?: number;
  page_size?: number;
}

/** 周边搜索结果 */
export interface NearbySearchResult {
  hospitals: Hospital[];
  total: number;
  page: number;
  page_size: number;
  center: Location;
  radius: number;
  mock?: boolean;
}

/** 推荐请求 */
export interface RecommendRequest {
  department: string;
  location: Location;
  limit?: number;
}

/** 推荐结果 */
export interface RecommendResult {
  department: string;
  hospitals: Hospital[];
  total: number;
}

/** 医院搜索 API */
export const hospitalApi = {
  /**
   * 搜索周边医院
   */
  async searchNearby(params: NearbySearchParams) {
    const queryParams = new URLSearchParams();
    queryParams.append("lat", params.lat.toString());
    queryParams.append("lng", params.lng.toString());
    if (params.keyword) queryParams.append("keyword", params.keyword);
    if (params.radius) queryParams.append("radius", params.radius.toString());
    if (params.page) queryParams.append("page", params.page.toString());
    if (params.page_size)
      queryParams.append("page_size", params.page_size.toString());

    const response = await get<NearbySearchResult>(
      `/hospital/nearby?${queryParams.toString()}`,
    );
    return response.data;
  },

  /**
   * 获取医院详情
   */
  async getDetail(poiId: string) {
    const response = await get<Hospital>(`/hospital/${poiId}`);
    return response.data;
  },

  /**
   * 基于科室推荐医院
   */
  async recommend(request: RecommendRequest) {
    const response = await post<RecommendResult>(
      "/hospital/recommend",
      request,
    );
    return response.data;
  },
};
