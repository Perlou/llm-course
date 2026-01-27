"""
MCP 协议介绍
===========

学习目标：
    1. 理解 MCP (Model Context Protocol) 概念
    2. 了解 MCP 架构和组件
    3. 理解 MCP 的应用场景

核心概念：
    - MCP：模型上下文协议
    - Server：提供工具和资源
    - Client：调用 Server 的服务
    - Transport：通信层

前置知识：
    - 01-10 所有 Agent 课程

环境要求：
    - pip install mcp python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：什么是 MCP ====================


def what_is_mcp():
    """什么是 MCP"""
    print("=" * 60)
    print("第一部分：什么是 MCP")
    print("=" * 60)

    print("""
    MCP (Model Context Protocol)
    ────────────────────────────
    
    MCP 是一个开放协议，用于标准化 AI 模型与外部工具/资源的交互。
    
    核心理念：
    ─────────
    • 将工具和资源封装为独立服务（Server）
    • 通过统一协议与 AI 模型交互
    • 解耦 AI 应用与具体实现
    
    ┌─────────────────────────────────────────────────────────┐
    │                     MCP 架构                            │
    │                                                         │
    │  ┌──────────┐       ┌──────────┐       ┌──────────┐    │
    │  │ AI 模型  │ ──→  │ MCP Client│ ──→  │MCP Server│    │
    │  │ (LLM)   │       │          │       │          │    │
    │  └──────────┘       └──────────┘       └──────────┘    │
    │                                              │          │
    │                                     ┌────────┴───────┐ │
    │                                     ▼        ▼       ▼ │
    │                                  [工具]  [资源]  [提示] │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    
    为什么需要 MCP？
    ───────────────
    ✅ 标准化：统一的工具调用协议
    ✅ 可复用：Server 可被多个 Client 使用
    ✅ 解耦：AI 应用与工具实现分离
    ✅ 生态：共享工具服务生态系统
    """)


# ==================== 第二部分：MCP 核心组件 ====================


def mcp_components():
    """MCP 核心组件"""
    print("\n" + "=" * 60)
    print("第二部分：MCP 核心组件")
    print("=" * 60)

    print("""
    MCP 核心组件
    ────────────
    
    1. Server（服务端）
       • 提供工具（Tools）
       • 提供资源（Resources）
       • 提供提示模板（Prompts）
    
    2. Client（客户端）
       • 连接 Server
       • 调用工具
       • 获取资源
    
    3. Transport（传输层）
       • stdio：标准输入输出
       • HTTP/SSE：网络通信
    
    MCP Server 能力
    ───────────────
    
    ┌─────────────────────────────────────────────┐
    │                MCP Server                    │
    │                                              │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
    │  │  Tools   │  │Resources │  │ Prompts  │  │
    │  │ (工具)   │  │ (资源)   │  │ (提示)   │  │
    │  └──────────┘  └──────────┘  └──────────┘  │
    │                                              │
    │  工具：可执行的操作（搜索、计算等）            │
    │  资源：静态内容（文档、数据等）               │
    │  提示：预定义的提示模板                      │
    │                                              │
    └─────────────────────────────────────────────┘
    """)


# ==================== 第三部分：MCP 通信流程 ====================


def mcp_communication():
    """MCP 通信流程"""
    print("\n" + "=" * 60)
    print("第三部分：MCP 通信流程")
    print("=" * 60)

    print("""
    MCP 通信流程
    ────────────
    
    1. 初始化连接
    ┌────────┐                    ┌────────┐
    │ Client │ ── initialize ──→ │ Server │
    │        │ ←── capabilities ──│        │
    └────────┘                    └────────┘
    
    2. 获取可用工具
    ┌────────┐                    ┌────────┐
    │ Client │ ── tools/list ──→ │ Server │
    │        │ ←── tool list ────│        │
    └────────┘                    └────────┘
    
    3. 调用工具
    ┌────────┐                    ┌────────┐
    │ Client │ ── tools/call ──→ │ Server │
    │        │ ←── result ───────│        │
    └────────┘                    └────────┘
    
    消息格式（JSON-RPC 2.0）
    ─────────────────────────
    
    请求：
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_weather",
            "arguments": {"city": "北京"}
        }
    }
    
    响应：
    {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "北京：晴，25°C"}]
        }
    }
    """)


# ==================== 第四部分：MCP 应用场景 ====================


def mcp_use_cases():
    """MCP 应用场景"""
    print("\n" + "=" * 60)
    print("第四部分：MCP 应用场景")
    print("=" * 60)

    print("""
    MCP 应用场景
    ────────────
    
    1. 文件系统访问
       • 读写本地文件
       • 目录遍历
       • 文件搜索
    
    2. 数据库操作
       • SQL 查询执行
       • 数据导入导出
       • 模式管理
    
    3. API 集成
       • 第三方服务调用
       • 数据获取和处理
    
    4. 开发工具
       • 代码分析
       • 项目管理
       • 测试执行
    
    典型 MCP Server 示例
    ────────────────────
    
    │ Server              │ 功能                    │
    ├─────────────────────┼────────────────────────┤
    │ filesystem          │ 文件读写操作            │
    │ sqlite              │ SQLite 数据库操作       │
    │ github              │ GitHub API 集成        │
    │ slack               │ Slack 消息发送         │
    │ web-search          │ 网络搜索               │
    """)


# ==================== 第五部分：MCP vs Function Calling ====================


def mcp_vs_function_calling():
    """MCP vs Function Calling"""
    print("\n" + "=" * 60)
    print("第五部分：MCP vs Function Calling")
    print("=" * 60)

    print("""
    MCP vs OpenAI Function Calling
    ──────────────────────────────
    
    │ 特性      │ Function Calling  │ MCP              │
    ├───────────┼──────────────────┼──────────────────┤
    │ 标准化    │ OpenAI 专有       │ 开放协议         │
    │ 可移植性  │ 绑定 OpenAI       │ 跨平台           │
    │ 工具复用  │ 需重复定义        │ Server 可共享    │
    │ 部署方式  │ 嵌入应用          │ 独立服务         │
    │ 生态系统  │ OpenAI 生态       │ 开放生态         │
    
    何时选择 MCP？
    ─────────────
    • 需要跨多个 AI 平台使用工具
    • 希望工具服务独立部署和管理
    • 需要与社区共享工具
    • 构建企业级 AI 应用
    
    何时选择 Function Calling？
    ─────────────────────────
    • 只使用 OpenAI API
    • 简单场景，快速原型
    • 工具逻辑简单，嵌入应用即可
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：了解 MCP 生态
        访问 https://modelcontextprotocol.io 
        了解现有的 MCP Server
    
    练习 2：对比分析
        列出你的项目适合用 MCP 还是 Function Calling
    
    思考题：
        MCP 如何确保工具调用的安全性？
        答：通过权限控制、沙箱执行、输入验证等机制
    """)


def main():
    print("🔌 MCP 协议介绍")
    print("=" * 60)

    what_is_mcp()
    mcp_components()
    mcp_communication()
    mcp_use_cases()
    mcp_vs_function_calling()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：12-mcp-server-basics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
