/**
 * 报告解读 API
 */

import type {
  ReportAnalysisResponse,
  IndicatorReference,
  ReportType,
} from "@medimind/types";
import { get, uploadFile, post } from "./client";

/** 报告解读 API */
export const reportApi = {
  /**
   * 上传并分析报告图片
   */
  async analyzeImage(file: File) {
    const response = await uploadFile<ReportAnalysisResponse>(
      "/report/analyze",
      file,
    );
    return response.data;
  },

  /**
   * 分析 Base64 编码的图片
   */
  async analyzeBase64(imageBase64: string, filename = "report.jpg") {
    const formData = new FormData();
    formData.append("image_base64", imageBase64);
    formData.append("filename", filename);

    const response = await fetch("/api/v1/report/analyze/base64", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`分析失败: ${response.status}`);
    }

    const result = await response.json();
    return result.data as ReportAnalysisResponse;
  },

  /**
   * 分析文本报告
   */
  async analyzeText(text: string) {
    const response = await post<ReportAnalysisResponse>(
      "/report/analyze/text",
      { text },
    );
    return response.data;
  },

  /**
   * 获取指标参考值
   */
  async getIndicatorReference(indicatorName: string) {
    const response = await get<IndicatorReference>(
      `/report/reference/${encodeURIComponent(indicatorName)}`,
    );
    return response.data;
  },

  /**
   * 获取所有指标参考值
   */
  async listReferences() {
    const response = await get<{
      references: IndicatorReference[];
      total: number;
    }>("/report/references");
    return response.data;
  },

  /**
   * 获取支持的报告类型
   */
  async listReportTypes() {
    const response = await get<{ types: ReportType[]; total: number }>(
      "/report/types",
    );
    return response.data;
  },
};
