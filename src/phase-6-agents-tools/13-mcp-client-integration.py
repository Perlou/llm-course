"""
MCP Client 集成
==============

学习目标：
    1. 掌握 MCP Client 使用方法
    2. 实现与 Server 的通信
    3. 将 MCP 集成到 Agent 中

核心概念：
    - Client Session：与 Server 的会话
    - Tool Discovery：发现可用工具
    - Tool Invocation：调用工具

前置知识：
    - 11-mcp-introduction.py
    - 12-mcp-server-basics.py

环境要求：
    - pip install mcp python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Client 基础 ====================


def client_basics():
    """Client 基础"""
    print("=" * 60)
    print("第一部分：MCP Client 基础")
    print("=" * 60)

    print("""
    MCP Client 工作流程
    ──────────────────
    
    1. 连接 Server
    2. 初始化会话
    3. 发现工具/资源
    4. 调用工具
    5. 关闭连接
    
    ┌────────────────────────────────────────────┐
    │              MCP Client 流程               │
    │                                            │
    │  ┌────────┐    连接    ┌────────┐         │
    │  │ Client │ ────────→ │ Server │         │
    │  └────────┘            └────────┘         │
    │       │                    │              │
    │       │  tools/list        │              │
    │       │───────────────────→│              │
    │       │←───────────────────│ tool list   │
    │       │                    │              │
    │       │  tools/call        │              │
    │       │───────────────────→│              │
    │       │←───────────────────│ result      │
    │       │                    │              │
    └────────────────────────────────────────────┘
    """)


# ==================== 第二部分：基础 Client 实现 ====================


def basic_client():
    """基础 Client 实现"""
    print("\n" + "=" * 60)
    print("第二部分：基础 Client 实现")
    print("=" * 60)

    code = """
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Server 配置
    server_params = StdioServerParameters(
        command="python",
        args=["my_server.py"]
    )
    
    # 连接 Server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()
            
            # 列出可用工具
            tools = await session.list_tools()
            print("可用工具：")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # 调用工具
            result = await session.call_tool(
                name="get_weather",
                arguments={"city": "北京"}
            )
            
            print(f"\\n工具返回：{result.content}")

if __name__ == "__main__":
    asyncio.run(main())
"""

    print("📌 基础 Client 代码：")
    print(code)


# ==================== 第三部分：封装 Client 类 ====================


def client_wrapper():
    """封装 Client 类"""
    print("\n" + "=" * 60)
    print("第三部分：封装 MCP Client 类")
    print("=" * 60)

    code = '''
class MCPClient:
    """MCP Client 封装"""
    
    def __init__(self, server_command: str, server_args: list):
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args
        )
        self.session = None
        self.tools = {}
    
    async def connect(self):
        """连接 Server"""
        self._read, self._write = await stdio_client(
            self.server_params
        ).__aenter__()
        
        self.session = ClientSession(self._read, self._write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        # 缓存工具列表
        result = await self.session.list_tools()
        self.tools = {t.name: t for t in result.tools}
    
    async def call(self, tool_name: str, **kwargs) -> str:
        """调用工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在: {tool_name}")
        
        result = await self.session.call_tool(
            name=tool_name,
            arguments=kwargs
        )
        
        return result.content[0].text
    
    async def close(self):
        """关闭连接"""
        if self.session:
            await self.session.__aexit__(None, None, None)

# 使用示例
async def demo():
    client = MCPClient("python", ["server.py"])
    await client.connect()
    
    result = await client.call("calculate", expression="10 * 5")
    print(f"计算结果: {result}")
    
    await client.close()
'''

    print("📌 封装后的 Client：")
    print(code)


# ==================== 第四部分：集成到 Agent ====================


def integrate_with_agent():
    """集成到 Agent"""
    print("\n" + "=" * 60)
    print("第四部分：集成到 Agent")
    print("=" * 60)

    code = '''
class MCPAgent:
    """集成 MCP 的 Agent"""
    
    def __init__(self, llm_client, mcp_client):
        self.llm = llm_client
        self.mcp = mcp_client
    
    async def setup(self):
        """初始化"""
        await self.mcp.connect()
        
        # 将 MCP 工具转换为 LLM 工具格式
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in self.mcp.tools.values()
        ]
    
    async def chat(self, message: str) -> str:
        """处理用户消息"""
        # 调用 LLM
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            tools=self.tools
        )
        
        msg = response.choices[0].message
        
        # 处理工具调用
        if msg.tool_calls:
            for tc in msg.tool_calls:
                result = await self.mcp.call(
                    tc.function.name,
                    **json.loads(tc.function.arguments)
                )
                # 将结果返回给 LLM...
        
        return msg.content
'''

    print("📌 MCP + Agent 集成：")
    print(code)

    print("""
    集成优势：
    ─────────
    ✅ 工具定义来自 MCP Server
    ✅ 工具实现与 Agent 解耦
    ✅ 可动态添加/移除工具
    """)


# ==================== 第五部分：多 Server 管理 ====================


def multi_server():
    """多 Server 管理"""
    print("\n" + "=" * 60)
    print("第五部分：多 Server 管理")
    print("=" * 60)

    print("""
    管理多个 MCP Server
    ──────────────────
    
    ┌─────────────────────────────────────────────┐
    │              Multi-Server Client            │
    │                                             │
    │  ┌────────────────────────────────────┐    │
    │  │         Server Manager              │    │
    │  └────────────────────────────────────┘    │
    │           │          │          │          │
    │           ▼          ▼          ▼          │
    │      ┌────────┐ ┌────────┐ ┌────────┐     │
    │      │ Files  │ │ Search │ │Database│     │
    │      │ Server │ │ Server │ │ Server │     │
    │      └────────┘ └────────┘ └────────┘     │
    │                                             │
    └─────────────────────────────────────────────┘
    
    实现思路：
    1. 维护 Server 名称到 Client 的映射
    2. 工具名添加 Server 前缀防止冲突
    3. 根据工具名路由到对应 Server
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现连接池
        管理多个 Server 连接，支持连接复用

        ✅ 参考答案：
        ```python
        from collections import defaultdict
        import asyncio

        class MCPConnectionPool:
            def __init__(self, max_connections: int = 5):
                self.max_connections = max_connections
                self.connections = {}
                self.available = defaultdict(list)
                self.lock = asyncio.Lock()

            async def get_connection(self, server_name: str):
                '''获取或创建连接'''
                async with self.lock:
                    # 检查是否有可用连接
                    if self.available[server_name]:
                        return self.available[server_name].pop()
                    
                    # 创建新连接
                    if len(self.connections.get(server_name, [])) < self.max_connections:
                        conn = await self.create_connection(server_name)
                        self.connections.setdefault(server_name, []).append(conn)
                        return conn
                    
                    raise RuntimeError("连接池已满")

            async def release(self, server_name: str, conn):
                '''释放连接回池'''
                async with self.lock:
                    self.available[server_name].append(conn)
        ```
    
    练习 2：添加重试机制
        工具调用失败时自动重试

        ✅ 参考答案：
        ```python
        import asyncio
        from functools import wraps

        def with_retry(max_retries: int = 3, delay: float = 1.0):
            def decorator(func):
                @wraps(func)
                async def wrapper(*args, **kwargs):
                    last_error = None
                    
                    for attempt in range(max_retries):
                        try:
                            return await func(*args, **kwargs)
                        except Exception as e:
                            last_error = e
                            if attempt < max_retries - 1:
                                wait = delay * (2 ** attempt)  # 指数退避
                                await asyncio.sleep(wait)
                    
                    raise last_error
                
                return wrapper
            return decorator

        @with_retry(max_retries=3)
        async def call_tool_with_retry(client, tool_name, args):
            return await client.call_tool(tool_name, args)
        ```
    
    练习 3：完整 Agent
        将 MCP Client 集成到完整的 ReAct Agent

        ✅ 参考答案：
        ```python
        class MCPReActAgent:
            def __init__(self, llm, mcp_client):
                self.llm = llm
                self.mcp = mcp_client

            async def run(self, query: str, max_steps: int = 5):
                tools = await self.mcp.list_tools()
                tools_desc = "\\n".join([f"- {t.name}: {t.description}" for t in tools])
                
                history = []
                for step in range(max_steps):
                    prompt = self.build_prompt(query, tools_desc, history)
                    response = self.llm.invoke(prompt).content
                    
                    if "Final Answer:" in response:
                        return self.extract_answer(response)
                    
                    tool_name, args = self.parse_action(response)
                    result = await self.mcp.call_tool(tool_name, args)
                    history.append({"action": tool_name, "result": result})
                
                return "达到最大步数"
        ```
    
    思考题：
        如何处理 Server 离线或超时？
        答：心跳检测、超时设置、自动重连

        ✅ 详细答案：
        ```python
        class ResilientMCPClient:
            def __init__(self, timeout: float = 30.0):
                self.timeout = timeout
                self.last_heartbeat = {}

            async def call_with_timeout(self, tool_name, args):
                try:
                    return await asyncio.wait_for(
                        self.client.call_tool(tool_name, args),
                        timeout=self.timeout
                    )
                except asyncio.TimeoutError:
                    await self.reconnect()
                    return await self.call_tool(tool_name, args)
        ```
    """)


def main():
    print("🔗 MCP Client 集成")
    print("=" * 60)

    client_basics()
    basic_client()
    client_wrapper()
    integrate_with_agent()
    multi_server()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：14-mcp-tools-resources.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
