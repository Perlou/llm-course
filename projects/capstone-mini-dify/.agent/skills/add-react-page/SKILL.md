---
name: add-react-page
description: 为 Mini-Dify 前端添加新的 React 页面
---

# 添加 React 页面技能

此技能用于在 Mini-Dify 前端应用中添加新的页面。

## 前端目录结构

```
frontend/src/
├── main.tsx                    # 渲染入口
├── App.tsx                     # 根组件 + 路由
├── index.css                   # 全局样式 + Tailwind
├── pages/                      # 页面组件
│   ├── ModelHub/               # 模型管理
│   │   └── index.tsx
│   ├── PromptStudio/           # Prompt 工坊
│   │   ├── index.tsx           # 列表页
│   │   └── Editor.tsx          # 编辑页
│   ├── Datasets/               # 知识库管理
│   │   ├── index.tsx           # 列表页
│   │   └── Detail.tsx          # 详情页
│   ├── AgentBuilder/           # Agent 构建
│   │   ├── index.tsx           # 列表页
│   │   └── Editor.tsx          # 编辑+Playground
│   ├── Workflow/               # 工作流
│   │   ├── index.tsx           # 列表页
│   │   └── Editor.tsx          # React Flow 画布
│   ├── Apps/                   # 应用管理
│   │   ├── index.tsx           # 列表页
│   │   └── Detail.tsx          # 详情+API Key
│   ├── Analytics/              # 监控面板
│   │   └── index.tsx
│   └── Playground/             # 测试游乐场
│       └── index.tsx
├── components/                 # 通用组件
│   ├── Layout/
│   │   ├── Sidebar.tsx         # 左侧导航
│   │   └── MainLayout.tsx      # 全局布局
│   ├── Chat/
│   │   ├── ChatWindow.tsx      # 对话窗口
│   │   └── ChatMessage.tsx     # 消息气泡
│   └── common/
│       ├── Card.tsx
│       ├── Modal.tsx
│       ├── Badge.tsx
│       └── StatsCard.tsx
├── services/                   # API 调用
│   └── api.ts
├── stores/                     # Zustand 状态管理
│   ├── modelStore.ts
│   └── workflowStore.ts
└── types/                      # TypeScript 类型
    └── index.ts
```

## 创建新页面步骤

### 1. 创建页面组件

```tsx
// src/pages/NewFeature/index.tsx
import { useState, useEffect } from "react";
import { Plus } from "lucide-react";

export default function NewFeaturePage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    setLoading(true);
    try {
      // const res = await api.getItems();
      // setItems(res.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">页面标题</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          新建
        </button>
      </div>

      {/* 内容区 */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          暂无数据，点击"新建"创建第一个
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
            >
              <h3 className="font-semibold text-slate-800">{item.name}</h3>
              <p className="text-sm text-slate-500 mt-1">{item.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 2. 添加路由

```tsx
// src/App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./components/Layout/MainLayout";
import NewFeaturePage from "./pages/NewFeature";

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          {/* 已有路由... */}
          <Route path="/new-feature" element={<NewFeaturePage />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}
```

### 3. 添加侧栏导航项

```tsx
// src/components/Layout/Sidebar.tsx
const navItems = [
  // 已有项...
  { icon: "✨", label: "新功能", path: "/new-feature" },
];
```

### 4. 添加 API 服务

```tsx
// src/services/api.ts
export const newFeatureApi = {
  list: () => apiClient.get("/api/v1/new-feature"),
  get: (id: string) => apiClient.get(`/api/v1/new-feature/${id}`),
  create: (data: any) => apiClient.post("/api/v1/new-feature", data),
  update: (id: string, data: any) =>
    apiClient.put(`/api/v1/new-feature/${id}`, data),
  delete: (id: string) => apiClient.delete(`/api/v1/new-feature/${id}`),
};
```

## 页面模板类型

### 列表页（卡片网格）

适用于：模型管理、Prompt 工坊、Agent 列表、应用管理

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map((item) => (
    <ItemCard key={item.id} {...item} />
  ))}
</div>
```

### 详情页（左右分栏）

适用于：Prompt 编辑、Agent 编辑（左配置右预览）

```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-80px)]">
  <div className="overflow-y-auto">左侧-配置面板</div>
  <div className="overflow-y-auto">右侧-预览/Playground</div>
</div>
```

### 三栏布局

适用于：工作流编辑器（左节点面板 + 中画布 + 右配置）

```tsx
<div className="flex h-[calc(100vh-80px)]">
  <div className="w-56 border-r">节点面板</div>
  <div className="flex-1">React Flow 画布</div>
  <div className="w-72 border-l">配置面板</div>
</div>
```

## 设计规范

### 颜色

| 用途     | Tailwind    | 色值    |
| -------- | ----------- | ------- |
| 主色     | indigo-500  | #6366F1 |
| 成功     | emerald-500 | #10B981 |
| 危险     | red-500     | #EF4444 |
| 侧栏背景 | 自定义      | #1E1E2E |
| 主区背景 | slate-50    | #F8FAFC |

### 字体

- 正文: `Inter` (Google Fonts)
- 代码: `JetBrains Mono`

### 响应式断点

| 断点 | 宽度       | 策略                 |
| ---- | ---------- | -------------------- |
| sm   | < 768px    | 侧栏折叠为 hamburger |
| md   | 768-1024px | 侧栏收窄为图标       |
| lg   | > 1024px   | 完整三栏布局         |
