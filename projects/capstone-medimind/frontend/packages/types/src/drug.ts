/**
 * 药品类型定义
 */

/** 药品信息 */
export interface DrugInfo {
  id: string;
  name: string;
  generic_name?: string;
  category?: string;
  is_otc: boolean;
  indications?: string;
  dosage?: string;
  side_effects?: string;
  contraindications?: string;
  interactions?: string;
  precautions?: string;
}

/** 药物相互作用结果 */
export interface InteractionResult {
  drug1: string;
  drug2: string;
  severity: "low" | "medium" | "high";
  description: string;
  recommendation: string;
}

/** 药品搜索响应 */
export interface DrugSearchResponse {
  drugs: DrugInfo[];
  total: number;
  query: string;
}

/** 药品列表响应 */
export interface DrugListResponse {
  drugs: DrugInfo[];
  total: number;
  limit: number;
  offset: number;
}

/** 相互作用检查响应 */
export interface InteractionCheckResponse {
  interactions: InteractionResult[];
  safe: boolean;
  checked_drugs: string[];
}
