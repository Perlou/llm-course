/**
 * 报告解读类型定义
 */

/** 指标状态 */
export type IndicatorStatus = "normal" | "high" | "low" | "critical";

/** 检验指标项 */
export interface IndicatorItem {
  name: string;
  value: string;
  unit: string;
  reference_range: string;
  status: IndicatorStatus;
  explanation: string;
}

/** 报告分析响应 */
export interface ReportAnalysisResponse {
  report_id: string;
  report_type: string;
  patient_info: Record<string, string>;
  test_date: string;
  indicators: IndicatorItem[];
  summary: string;
  recommendations: string[];
  warnings: string[];
  abnormal_count: number;
  critical_count: number;
}

/** 指标参考值 */
export interface IndicatorReference {
  name: string;
  normal_range: string;
  unit: string;
  description: string;
  high_meaning: string;
  low_meaning: string;
}

/** 报告类型 */
export interface ReportType {
  id: string;
  name: string;
  description: string;
}
