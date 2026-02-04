# MediMind API 设计文档

> 版本: 1.0  
> 基础路径: `/api/v1`

---

## 概述

MediMind API 提供健康问答、药品查询、报告解读和智能导诊四大功能模块。

### 通用响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "disclaimer": "仅供参考，不能替代专业医疗诊断"
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "Bad Request",
  "detail": "错误详情"
}
```

---

## 1. 健康问答 API

### POST /health/chat

发送健康问题并获取 AI 回答。

**请求**:

```json
{
  "query": "高血压应该注意什么?",
  "conversation_id": "optional-uuid"
}
```

**响应**:

```json
{
  "code": 200,
  "data": {
    "answer": "高血压患者应注意以下几点...",
    "sources": [
      {
        "title": "高血压防治指南",
        "source": "医学科普文档",
        "score": 0.89
      }
    ],
    "is_emergency": false,
    "conversation_id": "uuid",
    "disclaimer": "..."
  }
}
```

### POST /health/chat/stream

流式健康问答（SSE）。

### GET /health/history/{conversation_id}

获取对话历史。

### GET /health/conversations

获取最近对话列表。

### DELETE /health/conversation/{conversation_id}

删除对话。

---

## 2. 药品查询 API

### GET /drug/search

搜索药品。

**参数**:

- `q` (必填): 搜索关键词
- `limit` (可选): 结果数量，默认 10

**响应**:

```json
{
  "code": 200,
  "data": {
    "drugs": [
      {
        "id": "001",
        "name": "布洛芬缓释胶囊",
        "generic_name": "布洛芬",
        "category": "解热镇痛药",
        "is_otc": true,
        "indications": "用于缓解轻至中度疼痛..."
      }
    ],
    "total": 5
  }
}
```

### GET /drug/list

获取药品列表。

### GET /drug/{drug_id}

获取药品详情。

### POST /drug/interaction

检查药物相互作用。

**请求**:

```json
["阿司匹林", "布洛芬"]
```

**响应**:

```json
{
  "code": 200,
  "data": {
    "interactions": [
      {
        "drug1": "阿司匹林",
        "drug2": "布洛芬",
        "severity": "high",
        "description": "同时使用可能增加胃肠道出血风险",
        "recommendation": "建议避免同时使用，或在医生指导下用药"
      }
    ],
    "safe": false
  }
}
```

---

## 3. 报告解读 API

### POST /report/analyze

上传并分析报告图片。

**请求**: `multipart/form-data`

- `file`: 图片文件 (JPG/PNG)

**响应**:

```json
{
  "code": 200,
  "data": {
    "report_id": "uuid",
    "report_type": "血常规",
    "indicators": [
      {
        "name": "血红蛋白",
        "value": "165",
        "unit": "g/L",
        "reference_range": "130-175",
        "status": "normal",
        "explanation": "血红蛋白含量在正常范围内"
      }
    ],
    "summary": "总体指标正常，1项偏高",
    "recommendations": ["建议定期复查"],
    "abnormal_count": 1
  }
}
```

### POST /report/analyze/base64

分析 Base64 编码的图片。

### POST /report/analyze/text

分析文本格式报告。

---

## 4. 智能导诊 API

### POST /triage/start

开始导诊会话。

**响应**:

```json
{
  "code": 200,
  "data": {
    "session_id": "uuid",
    "state": "greeting",
    "message": "您好，我是智能导诊助手，请描述您的主要不适..."
  }
}
```

### POST /triage/{session_id}/chat

发送症状描述。

**请求**:

```json
{
  "message": "我头疼，发烧38度"
}
```

**响应**:

```json
{
  "code": 200,
  "data": {
    "session_id": "uuid",
    "state": "collecting",
    "urgency": "normal",
    "message": "请问头疼持续多长时间了？有没有其他症状？",
    "is_complete": false
  }
}
```

### GET /triage/{session_id}/status

获取会话状态。

### GET /triage/{session_id}/history

获取问诊历史。

### POST /triage/{session_id}/end

结束会话并获取推荐。

### GET /triage/departments

获取所有科室列表。

---

## 5. 系统 API

### GET /health

健康检查。

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 错误码说明

| 错误码 | 说明           |
| ------ | -------------- |
| 200    | 成功           |
| 400    | 请求参数错误   |
| 404    | 资源不存在     |
| 422    | 验证错误       |
| 500    | 服务器内部错误 |

---

## 安全说明

- 所有请求建议使用 HTTPS
- 敏感操作需要身份验证（待实现）
- API 调用频率限制：100 次/分钟
