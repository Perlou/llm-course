"""
MCP Server 开发基础
==================

学习目标：
    1. 掌握 MCP Server 开发流程
    2. 实现基础工具和资源
    3. 了解 Server 配置和部署

核心概念：
    - @server.tool()：定义工具
    - @server.resource()：定义资源
    - stdio transport：标准 IO 传输

前置知识：
    - 11-mcp-introduction.py

环境要求：
    - pip install mcp python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Server 基础结构 ====================


def server_structure():
    """Server 基础结构"""
    print("=" * 60)
    print("第一部分：MCP Server 基础结构")
    print("=" * 60)

    print("""
    MCP Server 基础结构
    ──────────────────
    
    一个最小的 MCP Server 包含：
    
    1. 创建 Server 实例
    2. 定义工具/资源
    3. 运行 Server
    
    ┌─────────────────────────────────────┐
    │         MCP Server 结构            │
    │                                    │
    │  ┌────────────────────────────┐   │
    │  │   from mcp.server import   │   │
    │  │       Server               │   │
    │  └────────────────────────────┘   │
    │               │                    │
    │               ▼                    │
    │  ┌────────────────────────────┐   │
    │  │   server = Server(name)    │   │
    │  └────────────────────────────┘   │
    │               │                    │
    │       ┌───────┴───────┐           │
    │       ▼               ▼           │
    │  ┌─────────┐    ┌─────────┐      │
    │  │ @tool   │    │@resource│      │
    │  └─────────┘    └─────────┘      │
    │               │                    │
    │               ▼                    │
    │  ┌────────────────────────────┐   │
    │  │      server.run()          │   │
    │  └────────────────────────────┘   │
    │                                    │
    └─────────────────────────────────────┘
    """)


# ==================== 第二部分：简单 Server 实现 ====================


def simple_server():
    """简单 Server 实现"""
    print("\n" + "=" * 60)
    print("第二部分：简单 MCP Server 实现")
    print("=" * 60)

    code = '''
# simple_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 创建 Server
server = Server("simple-tools")

# 定义工具
@server.tool()
async def get_weather(city: str) -> list[TextContent]:
    """获取城市天气
    
    Args:
        city: 城市名称
    """
    # 模拟天气数据
    weather = f"{city}: 晴，气温 25°C，湿度 60%"
    return [TextContent(type="text", text=weather)]

@server.tool()
async def calculate(expression: str) -> list[TextContent]:
    """执行数学计算
    
    Args:
        expression: 数学表达式
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        return [TextContent(type="text", text=f"计算错误: {e}")]

# 运行 Server
async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

    print("📌 简单 MCP Server 代码：")
    print(code)


# ==================== 第三部分：资源定义 ====================


def resource_definition():
    """资源定义"""
    print("\n" + "=" * 60)
    print("第三部分：定义资源 (Resources)")
    print("=" * 60)

    code = '''
from mcp.server import Server
from mcp.types import Resource, TextContent

server = Server("resource-server")

# 静态资源
KNOWLEDGE_BASE = {
    "python-basics": "Python 是一种解释型编程语言...",
    "mcp-intro": "MCP 是模型上下文协议...",
}

@server.list_resources()
async def list_resources() -> list[Resource]:
    """列出所有可用资源"""
    return [
        Resource(
            uri=f"docs://{key}",
            name=key,
            description=f"关于 {key} 的文档"
        )
        for key in KNOWLEDGE_BASE.keys()
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """读取资源内容"""
    # 解析 URI: docs://python-basics
    key = uri.replace("docs://", "")
    
    if key in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[key]
    
    raise ValueError(f"资源不存在: {uri}")
'''

    print("📌 资源定义代码：")
    print(code)

    print("""
    资源 vs 工具
    ────────────
    
    │ 特性     │ 资源 (Resource)  │ 工具 (Tool)     │
    ├──────────┼─────────────────┼────────────────┤
    │ 性质     │ 静态内容         │ 可执行操作      │
    │ 返回     │ 文本/数据        │ 执行结果        │
    │ 用途     │ 提供上下文       │ 完成任务        │
    """)


# ==================== 第四部分：工具参数验证 ====================


def parameter_validation():
    """工具参数验证"""
    print("\n" + "=" * 60)
    print("第四部分：参数验证")
    print("=" * 60)

    code = '''
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import TextContent

server = Server("validated-tools")

# 使用 Pydantic 定义参数
class SearchParams(BaseModel):
    query: str = Field(..., description="搜索关键词")
    max_results: int = Field(default=10, ge=1, le=100)
    language: str = Field(default="zh", pattern="^(zh|en)$")

@server.tool()
async def search(
    query: str,
    max_results: int = 10,
    language: str = "zh"
) -> list[TextContent]:
    """搜索信息
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数 (1-100)
        language: 语言 (zh/en)
    """
    # 验证参数
    params = SearchParams(
        query=query,
        max_results=max_results,
        language=language
    )
    
    result = f"搜索 '{params.query}' 的 {params.max_results} 条结果..."
    return [TextContent(type="text", text=result)]
'''

    print("📌 参数验证代码：")
    print(code)


# ==================== 第五部分：配置和部署 ====================


def configuration():
    """配置和部署"""
    print("\n" + "=" * 60)
    print("第五部分：配置和部署")
    print("=" * 60)

    print("""
    Claude Desktop 配置
    ────────────────────
    
    在 claude_desktop_config.json 中添加：
    
    {
        "mcpServers": {
            "my-tools": {
                "command": "python",
                "args": ["/path/to/my_server.py"]
            }
        }
    }
    
    配置位置：
    • macOS: ~/Library/Application Support/Claude/
    • Windows: %APPDATA%/Claude/
    
    运行模式
    ────────
    
    1. stdio 模式（推荐）
       通过标准输入输出通信
       适合本地部署
    
    2. HTTP/SSE 模式
       通过网络通信
       适合远程部署
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建文件工具 Server
        实现 read_file 和 list_dir 工具
    
    练习 2：添加错误处理
        为工具添加完善的错误处理和日志
    
    练习 3：测试 Server
        使用 MCP Inspector 或编写测试用例
    
    思考题：
        如何确保 MCP Server 的安全性？
        答：限制文件路径、验证输入、添加权限控制
    """)


def main():
    print("🔨 MCP Server 开发基础")
    print("=" * 60)

    server_structure()
    simple_server()
    resource_definition()
    parameter_validation()
    configuration()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：13-mcp-client-integration.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
