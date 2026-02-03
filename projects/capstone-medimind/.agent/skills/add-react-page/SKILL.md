---
name: add-react-page
description: 为 MediMind Web 应用添加新的 React 页面
---

# 添加 React 页面技能

此技能用于在 MediMind Web 应用 (`apps/web`) 中添加新的页面。

## 页面结构

```
frontend/apps/web/src/
├── App.tsx                   # 应用入口，路由配置
├── main.tsx                  # 渲染入口
├── pages/                    # 页面组件
│   ├── HomePage.tsx          # 首页
│   ├── HealthQAPage.tsx      # 健康问答
│   ├── DrugSearchPage.tsx    # 药品查询
│   ├── ReportPage.tsx        # 报告解读
│   └── TriagePage.tsx        # 智能导诊
├── routes/                   # 路由配置
│   └── index.tsx
├── hooks/                    # 自定义 Hooks
│   └── useChat.ts
├── stores/                   # 状态管理
│   └── chatStore.ts
└── styles/
    └── globals.css
```

## 创建新页面步骤

### 1. 创建页面组件

```tsx
// src/pages/NewPage.tsx
import React, { useState, useEffect } from "react";
import { SafetyBanner, Card, Button } from "@medimind/ui";
import { someApi } from "@medimind/api-client";

export function NewPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 安全横幅 */}
      <SafetyBanner />

      {/* 页面内容 */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">页面标题</h1>

        {/* 主要内容区域 */}
        <Card className="p-6">{/* 内容 */}</Card>
      </main>

      {/* 页脚免责声明 */}
      <footer className="text-center text-sm text-gray-500 py-4">
        以上信息仅供参考，如有健康问题请咨询专业医生
      </footer>
    </div>
  );
}
```

### 2. 添加路由

```tsx
// src/routes/index.tsx
import { createBrowserRouter } from "react-router-dom";
import { HomePage } from "../pages/HomePage";
import { HealthQAPage } from "../pages/HealthQAPage";
import { NewPage } from "../pages/NewPage";

export const router = createBrowserRouter([
  { path: "/", element: <HomePage /> },
  { path: "/health", element: <HealthQAPage /> },
  { path: "/new-feature", element: <NewPage /> },
]);
```

### 3. 在 App.tsx 使用路由

```tsx
// src/App.tsx
import { RouterProvider } from "react-router-dom";
import { router } from "./routes";

export function App() {
  return <RouterProvider router={router} />;
}
```

## MediMind 页面模板

### 健康问答页面

```tsx
// src/pages/HealthQAPage.tsx
import React, { useState, useRef, useEffect } from "react";
import {
  SafetyBanner,
  ChatMessage,
  EmergencyAlert,
  Button,
  Input,
} from "@medimind/ui";
import { healthApi } from "@medimind/api-client";
import type { ChatResponse } from "@medimind/types";
import { Send } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ title: string; page?: string }>;
}

export function HealthQAPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [emergency, setEmergency] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = (await healthApi.chat(input)) as ChatResponse;

      if (response.emergency) {
        setEmergency(true);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <SafetyBanner />
      <EmergencyAlert show={emergency} onClose={() => setEmergency(false)} />

      {/* 消息区域 */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <h2 className="text-xl font-semibold text-gray-700">
                👋 您好，有什么健康问题可以帮您？
              </h2>
              <p className="text-gray-500 mt-2">
                例如：高血压应该注意什么？感冒了怎么办？
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              content={msg.content}
              isUser={msg.role === "user"}
              sources={msg.sources}
            />
          ))}

          {loading && <ChatMessage content="" isUser={false} isLoading />}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* 输入区域 */}
      <footer className="border-t bg-white px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="输入您的健康问题..."
            disabled={loading}
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={loading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </footer>
    </div>
  );
}
```

### 报告解读页面

```tsx
// src/pages/ReportPage.tsx
import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { SafetyBanner, Card, Button } from "@medimind/ui";
import { reportApi } from "@medimind/api-client";
import { Upload, FileImage, Loader2 } from "lucide-react";

export function ReportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png"] },
    maxFiles: 1,
  });

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("image", file);
      const response = await reportApi.analyze(formData);
      setResult(response);
    } catch (error) {
      console.error("Analyze error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SafetyBanner />

      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">📋 报告解读</h1>

        <div className="grid md:grid-cols-2 gap-6">
          {/* 上传区域 */}
          <Card className="p-6">
            <h2 className="font-semibold mb-4">上传报告图片</h2>

            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                transition-colors
                ${isDragActive ? "border-teal-500 bg-teal-50" : "border-gray-300 hover:border-teal-400"}
              `}
            >
              <input {...getInputProps()} />
              {preview ? (
                <img
                  src={preview}
                  alt="预览"
                  className="max-h-48 mx-auto rounded-lg"
                />
              ) : (
                <>
                  <FileImage className="w-12 h-12 mx-auto text-gray-400 mb-3" />
                  <p className="text-gray-600">拖放图片到这里，或点击上传</p>
                  <p className="text-sm text-gray-400 mt-1">
                    支持 JPG, PNG 格式
                  </p>
                </>
              )}
            </div>

            <Button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="w-full mt-4"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  分析中...
                </>
              ) : (
                "开始分析"
              )}
            </Button>
          </Card>

          {/* 结果区域 */}
          <Card className="p-6">
            <h2 className="font-semibold mb-4">分析结果</h2>

            {result ? (
              <div className="space-y-4">
                {/* 异常指标提醒 */}
                {result.abnormal_count > 0 && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <p className="text-amber-800">
                      ⚠️ 发现 {result.abnormal_count} 项异常指标
                    </p>
                  </div>
                )}

                {/* 指标列表 */}
                <div className="space-y-2">
                  {result.items?.map((item: any, i: number) => (
                    <div
                      key={i}
                      className={`
                        p-3 rounded-lg border
                        ${item.status === "NORMAL" ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}
                      `}
                    >
                      <div className="flex justify-between">
                        <span className="font-medium">{item.name}</span>
                        <span>
                          {item.value} {item.unit}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        参考范围: {item.normal_range}
                      </p>
                    </div>
                  ))}
                </div>

                {/* 综合解读 */}
                <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                  <h3 className="font-medium mb-2">综合解读</h3>
                  <p className="text-gray-700">{result.summary}</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                上传报告图片后将在这里显示分析结果
              </p>
            )}
          </Card>
        </div>

        <p className="text-center text-sm text-gray-500 mt-8">
          ⚕️ 报告解读仅供参考，如有异常指标建议咨询专业医生
        </p>
      </main>
    </div>
  );
}
```

## 页面结构规范

每个页面应包含：

1. **SafetyBanner** - 顶部安全提示横幅
2. **主要内容区域** - `max-w-4xl mx-auto` 居中布局
3. **免责声明** - 页脚或结果末尾
4. **紧急提醒** - 需要时显示 EmergencyAlert

## 响应式布局

```tsx
// 使用 Tailwind 响应式类
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* 内容 */}
</div>

// 移动端优先
<div className="px-4 md:px-6 lg:px-8">
  {/* 内容 */}
</div>
```

## 注意事项

1. **医疗合规**：每个页面必须包含免责声明
2. **紧急处理**：检测到紧急症状时显示 EmergencyAlert
3. **加载状态**：所有 API 调用需有加载状态
4. **错误处理**：优雅处理 API 错误
5. **无障碍**：使用语义化 HTML 标签
