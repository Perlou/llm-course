# MediMind 项目摘要

> 最后更新: 2026-02-05

## 📊 项目状态

**状态**: ✅ 开发完成  
**版本**: 1.0.0  
**开发周期**: 2026-02-03 ~ 2026-02-05

---

## 🎯 项目概述

MediMind 是一款面向患者的智能健康信息服务平台，基于 RAG + Agent + 多模态技术，提供健康咨询、药品查询、报告解读、智能导诊等功能。

---

## ✅ 已完成功能

### 核心功能

| 功能     | 技术                          | 状态 |
| -------- | ----------------------------- | ---- |
| 健康问答 | RAG (ChromaDB + BGE + Gemini) | ✅   |
| 药品查询 | 向量检索 + JSON 数据库        | ✅   |
| 报告解读 | Gemini Vision 多模态          | ✅   |
| 智能导诊 | LangGraph Agent               | ✅   |
| 安全护栏 | 规则引擎                      | ✅   |

### 扩展功能

| 功能     | 说明                | 状态 |
| -------- | ------------------- | ---- |
| 用户认证 | 注册/登录 (JWT)     | ✅   |
| 健康档案 | 个人信息 + 健康记录 | ✅   |
| 附近医院 | 高德地图 POI 搜索   | ✅   |
| 提醒管理 | 用药/复查提醒       | ✅   |

---

## 🛠️ 技术架构

### 后端

- **框架**: FastAPI
- **向量库**: ChromaDB
- **嵌入模型**: sentence-transformers (BGE)
- **LLM**: Google Gemini
- **认证**: PyJWT

### 前端

- **架构**: Turborepo Monorepo
- **框架**: React 18 + TypeScript
- **构建**: Vite
- **路由**: React Router

---

## 📁 项目结构

```
capstone-medimind/
├── src/                # 后端 (FastAPI)
├── frontend/           # 前端 (Turborepo)
├── data/               # 数据文件
├── tests/              # 测试用例
├── docs/               # 文档
├── start.sh            # 启动脚本
├── stop.sh             # 停止脚本
└── requirements.txt    # 依赖
```

---

## 📈 测试覆盖

| 测试文件         | 测试数 | 状态 |
| ---------------- | ------ | ---- |
| test_auth.py     | 13     | ✅   |
| test_profile.py  | 11     | ✅   |
| test_reminder.py | 9      | ✅   |
| **总计**         | **33** | ✅   |

---

## 🚀 启动方式

```bash
./start.sh   # 启动
./stop.sh    # 停止
./status.sh  # 状态
```

---

## 📚 文档

- [README.md](../README.md) - 项目说明
- [PRD.md](PRD.md) - 产品需求
- [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) - 技术设计
- [API_DESIGN.md](API_DESIGN.md) - API 规范
- [USER_GUIDE.md](USER_GUIDE.md) - 用户指南
- [PROGRESS_TRACKER.md](PROGRESS_TRACKER.md) - 开发进度
