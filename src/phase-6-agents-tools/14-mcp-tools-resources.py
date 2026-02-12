"""
MCP 实战应用
===========

学习目标：
    1. 构建完整的 MCP 工具服务
    2. 实现实用工具集
    3. 端到端 MCP Agent 应用

核心概念：
    - 文件系统工具
    - 数据库工具
    - 完整应用示例

前置知识：
    - 11-13 所有 MCP 课程

环境要求：
    - pip install mcp python-dotenv aiosqlite
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：文件系统 Server ====================


def filesystem_server():
    """文件系统 Server"""
    print("=" * 60)
    print("第一部分：文件系统 MCP Server")
    print("=" * 60)

    code = '''
# filesystem_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent
import os

server = Server("filesystem")
ALLOWED_DIR = os.path.expanduser("~/documents")

@server.tool()
async def read_file(path: str) -> list[TextContent]:
    """读取文件内容
    
    Args:
        path: 文件路径（相对于 documents 目录）
    """
    full_path = os.path.join(ALLOWED_DIR, path)
    
    # 安全检查
    if not full_path.startswith(ALLOWED_DIR):
        return [TextContent(type="text", text="错误：非法路径")]
    
    if not os.path.exists(full_path):
        return [TextContent(type="text", text="错误：文件不存在")]
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return [TextContent(type="text", text=content)]

@server.tool()
async def list_dir(path: str = ".") -> list[TextContent]:
    """列出目录内容
    
    Args:
        path: 目录路径
    """
    full_path = os.path.join(ALLOWED_DIR, path)
    
    if not os.path.isdir(full_path):
        return [TextContent(type="text", text="错误：不是目录")]
    
    items = os.listdir(full_path)
    result = "\\n".join(items)
    
    return [TextContent(type="text", text=result)]

@server.tool()
async def write_file(path: str, content: str) -> list[TextContent]:
    """写入文件
    
    Args:
        path: 文件路径
        content: 文件内容
    """
    full_path = os.path.join(ALLOWED_DIR, path)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return [TextContent(type="text", text=f"已写入: {path}")]
'''

    print("📌 文件系统 Server：")
    print(code)


# ==================== 第二部分：SQLite Server ====================


def sqlite_server():
    """SQLite Server"""
    print("\n" + "=" * 60)
    print("第二部分：SQLite MCP Server")
    print("=" * 60)

    code = '''
# sqlite_server.py
from mcp.server import Server
from mcp.types import TextContent, Resource
import aiosqlite
import json

server = Server("sqlite")
DB_PATH = "data.db"

@server.tool()
async def query(sql: str) -> list[TextContent]:
    """执行 SQL 查询（只读）
    
    Args:
        sql: SQL 查询语句
    """
    # 安全检查：只允许 SELECT
    if not sql.strip().upper().startswith("SELECT"):
        return [TextContent(type="text", text="只允许 SELECT 查询")]
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(sql)
        rows = await cursor.fetchall()
        columns = [d[0] for d in cursor.description]
    
    result = [dict(zip(columns, row)) for row in rows]
    return [TextContent(type="text", text=json.dumps(result))]

@server.tool()
async def list_tables() -> list[TextContent]:
    """列出所有表"""
    sql = "SELECT name FROM sqlite_master WHERE type='table'"
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(sql)
        tables = await cursor.fetchall()
    
    result = [t[0] for t in tables]
    return [TextContent(type="text", text=json.dumps(result))]

@server.list_resources()
async def list_resources() -> list[Resource]:
    """列出数据库表作为资源"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = await cursor.fetchall()
    
    return [
        Resource(
            uri=f"sqlite://{t[0]}",
            name=t[0],
            description=f"数据表: {t[0]}"
        )
        for t in tables
    ]
'''

    print("📌 SQLite Server：")
    print(code)


# ==================== 第三部分：完整 Agent 应用 ====================


def complete_agent():
    """完整 Agent 应用"""
    print("\n" + "=" * 60)
    print("第三部分：完整 MCP Agent 应用")
    print("=" * 60)

    code = '''
# mcp_agent.py
import google.generativeai as genai
import asyncio
import json

class MCPReActAgent:
    """集成 MCP 的 ReAct Agent"""
    
    def __init__(self, mcp_clients: dict):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.llm = genai.GenerativeModel('gemini-2.0-flash')
        self.mcp_clients = mcp_clients  # {name: client}
        self.tools = []
        self.tool_map = {}  # tool_name -> (client, original_name)
    
    async def setup(self):
        """初始化所有 MCP 连接"""
        for name, client in self.mcp_clients.items():
            await client.connect()
            
            # 注册工具，添加前缀防止冲突
            for tool in client.tools.values():
                full_name = f"{name}_{tool.name}"
                self.tool_map[full_name] = (client, tool.name)
                
                self.tools.append({
                    "type": "function",
                    "function": {
                        "name": full_name,
                        "description": f"[{name}] {tool.description}",
                        "parameters": tool.inputSchema
                    }
                })
    
    async def chat(self, message: str) -> str:
        """处理用户消息"""
        messages = [{"role": "user", "content": message}]
        
        for _ in range(5):  # 最多 5 轮
            response = self.llm.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=self.tools
            )
            
            msg = response.choices[0].message
            
            if not msg.tool_calls:
                return msg.content
            
            messages.append(msg)
            
            for tc in msg.tool_calls:
                client, orig_name = self.tool_map[tc.function.name]
                
                result = await client.call(
                    orig_name,
                    **json.loads(tc.function.arguments)
                )
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        
        return "达到最大轮数"

# 使用示例
async def main():
    # 创建 MCP Clients
    fs_client = MCPClient("python", ["filesystem_server.py"])
    db_client = MCPClient("python", ["sqlite_server.py"])
    
    # 创建 Agent
    agent = MCPReActAgent({
        "fs": fs_client,
        "db": db_client
    })
    
    await agent.setup()
    
    # 对话
    result = await agent.chat(
        "查看 documents 目录下的文件列表"
    )
    print(result)
'''

    print("📌 完整 MCP Agent：")
    print(code)


# ==================== 第四部分：最佳实践 ====================


def best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("第四部分：MCP 最佳实践")
    print("=" * 60)

    print("""
    MCP 开发最佳实践
    ────────────────
    
    1. 安全性
       ✅ 路径白名单
       ✅ 输入验证
       ✅ 权限控制
       ✅ 只读操作优先
    
    2. 错误处理
       ✅ 详细错误信息
       ✅ 优雅降级
       ✅ 重试机制
    
    3. 性能
       ✅ 连接池复用
       ✅ 异步操作
       ✅ 响应缓存
    
    4. 可观测性
       ✅ 详细日志
       ✅ 调用追踪
       ✅ 性能监控
    
    5. 工具设计
       ✅ 单一职责
       ✅ 清晰描述
       ✅ 合理参数
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：构建 GitHub MCP Server
        实现 list_repos、get_file、search_code 工具

        ✅ 参考答案：
        ```python
        from mcp.server import Server
        import aiohttp
        import os

        server = Server("github-tools")
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

        @server.tool()
        async def list_repos(username: str) -> str:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/users/{username}/repos"
                async with session.get(url, headers=HEADERS) as resp:
                    repos = await resp.json()
                    return "\\n".join([r["full_name"] for r in repos[:10]])

        @server.tool()
        async def get_file(repo: str, path: str) -> str:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/repos/{repo}/contents/{path}"
                async with session.get(url, headers=HEADERS) as resp:
                    data = await resp.json()
                    import base64
                    return base64.b64decode(data["content"]).decode()

        @server.tool()
        async def search_code(query: str, repo: str = None) -> str:
            q = f"{query} repo:{repo}" if repo else query
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/search/code?q={q}"
                async with session.get(url, headers=HEADERS) as resp:
                    data = await resp.json()
                    items = data.get("items", [])[:5]
                    return "\\n".join([f"{i['path']} in {i['repository']['full_name']}" for i in items])
        ```
    
    练习 2：构建天气 MCP Server
        调用真实天气 API

        ✅ 参考答案：
        ```python
        from mcp.server import Server
        import aiohttp
        import os

        server = Server("weather-tools")
        API_KEY = os.getenv("OPENWEATHER_API_KEY")

        @server.tool()
        async def get_weather(city: str) -> str:
            '''获取城市天气'''
            async with aiohttp.ClientSession() as session:
                url = f"https://api.openweathermap.org/data/2.5/weather"
                params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "zh_cn"}
                
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    
                    if resp.status == 200:
                        return f"{city}: {data['weather'][0]['description']}, 温度 {data['main']['temp']}°C"
                    return f"获取失败: {data.get('message', '未知错误')}"

        @server.tool()
        async def get_forecast(city: str, days: int = 3) -> str:
            '''获取天气预报'''
            async with aiohttp.ClientSession() as session:
                url = f"https://api.openweathermap.org/data/2.5/forecast"
                params = {"q": city, "appid": API_KEY, "units": "metric", "cnt": days * 8}
                
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    forecasts = []
                    for item in data["list"][::8]:  # 每天一条
                        forecasts.append(f"{item['dt_txt']}: {item['main']['temp']}°C")
                    return "\\n".join(forecasts)
        ```
    
    练习 3：完整研究助手
        结合文件、搜索、数据库构建研究助手 Agent

        ✅ 参考答案：
        ```python
        class ResearchAssistant:
            def __init__(self, llm, servers: dict):
                self.llm = llm
                self.servers = servers  # {"file": file_client, "search": search_client, "db": db_client}

            async def research(self, topic: str):
                '''执行研究流程'''
                # 1. 搜索相关资料
                search_results = await self.servers["search"].call_tool(
                    "search", {"query": topic}
                )
                
                # 2. 保存笔记
                notes = self.llm.invoke(f"总结：{search_results}").content
                await self.servers["file"].call_tool(
                    "write_file", {"path": f"/notes/{topic}.md", "content": notes}
                )
                
                # 3. 存储引用
                await self.servers["db"].call_tool(
                    "insert", {"table": "references", "data": {"topic": topic, "notes": notes}}
                )
                
                return notes
        ```

    实战项目：自动化研究助手
    ──────────────────────
    构建能够自动搜索、阅读、总结文献的研究助手：
    
    1. 搜索 Server：获取研究资料
    2. 文件 Server：保存笔记
    3. 数据库 Server：管理引用
    4. Agent：协调所有工具完成研究任务

        ✅ 架构设计：
        ```
        ┌─────────────────────────────────────────────┐
        │              Research Agent                  │
        │  (协调 LLM + MCP Clients)                   │
        └─────────────┬───────────────────────────────┘
                      │
        ┌─────────────┴───────────────────────────────┐
        │           MCP Client Hub                     │
        └──────┬──────────┬──────────────┬────────────┘
               │          │              │
        ┌──────▼──┐ ┌─────▼────┐ ┌───────▼──────┐
        │ Search  │ │  File    │ │   Database   │
        │ Server  │ │  Server  │ │   Server     │
        └─────────┘ └──────────┘ └──────────────┘
        ```
    """)


# ==================== 第六部分：总结 ====================


def summary():
    """总结"""
    print("\n" + "=" * 60)
    print("Phase 6 总结")
    print("=" * 60)

    print("""
    🎉 恭喜完成 Phase 6！
    
    你已掌握：
    ──────────
    ✅ Agent 架构和核心概念
    ✅ ReAct、Plan-Execute、Self-Ask 模式
    ✅ 工具定义、调用和路由
    ✅ Gemini Function Calling
    ✅ Agent 记忆管理
    ✅ MCP 协议和 Server/Client 开发
    
    下一步：
    ────────
    • 构建完整的 Agent 应用
    • 探索 Multi-Agent 协作
    • 学习 Agent 评估和优化
    • 了解 Agent 安全和对齐
    """)


def main():
    print("🚀 MCP 实战应用")
    print("=" * 60)

    filesystem_server()
    sqlite_server()
    complete_agent()
    best_practices()
    exercises()
    summary()

    print("\n" + "=" * 60)
    print("✅ Phase 6 全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
