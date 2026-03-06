---
name: update-progress
description: 更新 Mini-Dify 项目开发进度
---

# 更新开发进度技能

此技能用于更新 Mini-Dify 项目的开发进度追踪。

## 进度文件位置

```
/Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify/docs/PROGRESS_TRACKER.md
```

## 状态标记

| 图标 | 状态   | 说明     |
| ---- | ------ | -------- |
| ⬜   | 待开始 | 尚未开始 |
| 🔄   | 进行中 | 正在开发 |
| ✅   | 已完成 | 开发完成 |
| ⚠️   | 阻塞   | 遇到问题 |
| ⏭️   | 跳过   | 任务跳过 |

## 更新任务状态

### 开始任务

将状态从 `⬜ 待开始` 改为 `🔄 进行中`：

```markdown
| 1.3 | Docker Compose (PostgreSQL + Milvus) | 1h | 🔄 进行中 | | |
```

### 完成任务

将状态改为 `✅ 已完成`，填写完成日期：

```markdown
| 1.3 | Docker Compose (PostgreSQL + Milvus) | 1h | ✅ 已完成 | 03-07 | |
```

## 更新统计表

完成任务后更新 "进度统计" 部分：

```markdown
| 阶段     | 总任务数 | 已完成 | 进行中 | 完成率 |
| -------- | -------- | ------ | ------ | ------ |
| Phase 1  | 10       | 5      | 1      | 50%    |
| Phase 2  | 8        | 0      | 0      | 0%     |
| **总计** | **58**   | **5**  | **1**  | **9%** |
```

## 添加每日日志

在 "每日更新日志" 部分添加：

```markdown
### 2026-03-07

- ✅ 完成 Docker Compose 配置 (PostgreSQL + Milvus)
- ✅ 完成后端骨架搭建 (FastAPI + SQLAlchemy)
- 🔄 正在定义数据库模型
- 📝 Milvus 单机版启动较慢，考虑 Milvus Lite 作为开发替代
```

## 更新风险追踪

遇到问题时记录：

```markdown
| 风险               | 状态      | 描述                | 缓解措施               |
| ------------------ | --------- | ------------------- | ---------------------- |
| 工作流编辑器复杂度 | ⬜ 待观察 | React Flow 学习曲线 | 提前学习，参考 Flowise |
| Milvus 内存占用    | 🔄 处理中 | 开发环境内存不足    | 使用 Milvus Lite 开发  |
```

## 更新交付物

完成后勾选交付物：

```markdown
**交付物**:

- [x] Docker 基础服务 (PostgreSQL + Milvus)
- [x] 后端骨架 (FastAPI + SQLAlchemy + Alembic 迁移)
- [ ] 前端骨架 (Vite + React + Tailwind + 路由)
- [ ] 全局布局 (侧栏导航 + 主内容区)
```

## 阶段完成检查

每个阶段完成时：

1. ✅ 所有任务标记为完成
2. ✅ 所有交付物已勾选
3. ✅ 统计表数据更新
4. ✅ 在每日日志记录完成
5. ✅ 阶段状态改为 `✅ 已完成`

## 时间统计

更新已投入工时：

```markdown
| 指标       | 值        |
| ---------- | --------- |
| 预计总工时 | ~98 小时  |
| 已投入工时 | ~15 小时  |
| 项目状态   | 🔄 开发中 |
```
