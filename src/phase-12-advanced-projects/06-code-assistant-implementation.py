"""
代码助手 - 完整实现
==================

学习目标：
    1. 实现代码补全和生成服务
    2. 构建代码上下文管理器
    3. 集成代码分析工具

本文件包含核心实现代码参考
"""


# ==================== 项目结构 ====================

PROJECT_STRUCTURE = """
code-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── completion.py       # 代码补全
│   │   ├── generation.py       # 代码生成
│   │   ├── explanation.py      # 代码解释
│   │   └── review.py           # 代码评审
│   │
│   ├── services/
│   │   ├── context_service.py  # 上下文管理
│   │   ├── code_analyzer.py    # 代码分析
│   │   ├── llm_service.py      # LLM 调用
│   │   └── cache_service.py    # 缓存服务
│   │
│   ├── models/
│   │   └── request.py          # 请求模型
│   │
│   └── prompts/                # Prompt 模板
│       ├── completion.py
│       ├── generation.py
│       └── review.py
│
├── extensions/
│   └── vscode/                 # VSCode 插件
│
└── tests/
"""

print("=" * 60)
print("第一部分：项目结构")
print("=" * 60)
print(PROJECT_STRUCTURE)


# ==================== 上下文服务 ====================

CONTEXT_SERVICE = '''
# app/services/context_service.py
from dataclasses import dataclass
from typing import List, Optional, Dict
import os

@dataclass
class CodeContext:
    """代码上下文"""
    file_path: str
    language: str
    cursor_line: int
    cursor_column: int

    # 当前文件
    file_content: str
    prefix: str  # 光标前的代码
    suffix: str  # 光标后的代码

    # 结构信息
    imports: List[str] = None
    current_function: Optional[str] = None
    current_class: Optional[str] = None

    # 相关上下文
    related_files: List[Dict] = None

class ContextService:
    """上下文管理服务"""

    MAX_CONTEXT_TOKENS = 6000

    def __init__(self, code_analyzer, index_service):
        self.analyzer = code_analyzer
        self.index_service = index_service

    async def build_context(
        self,
        file_path: str,
        file_content: str,
        cursor_line: int,
        cursor_column: int,
        language: str
    ) -> CodeContext:
        """构建完整的代码上下文"""

        # 分割 prefix 和 suffix
        lines = file_content.split("\\n")
        prefix_lines = lines[:cursor_line]
        suffix_lines = lines[cursor_line:]

        if cursor_line < len(lines):
            current_line = lines[cursor_line]
            prefix_lines[-1] = current_line[:cursor_column] if cursor_line > 0 else ""
            suffix_lines[0] = current_line[cursor_column:]

        prefix = "\\n".join(prefix_lines)
        suffix = "\\n".join(suffix_lines)

        # 分析代码结构
        analysis = self.analyzer.get_cursor_context(
            file_content, cursor_line, cursor_column
        )

        # 提取导入
        imports = self.analyzer.get_imports(file_content)

        # 检索相关文件
        related = await self._get_related_files(file_path, file_content, language)

        return CodeContext(
            file_path=file_path,
            language=language,
            cursor_line=cursor_line,
            cursor_column=cursor_column,
            file_content=file_content,
            prefix=prefix,
            suffix=suffix,
            imports=[str(imp) for imp in imports],
            current_function=analysis.get("parent_function"),
            current_class=analysis.get("parent_class"),
            related_files=related
        )

    async def _get_related_files(
        self,
        file_path: str,
        content: str,
        language: str
    ) -> List[Dict]:
        """获取相关文件"""
        related = []

        # 基于导入关系
        imports = self.analyzer.get_imports(content)
        for imp in imports[:5]:  # 限制数量
            # 解析导入路径，查找对应文件
            pass

        # 基于语义相似度（可选）
        # similar_files = await self.index_service.search_similar(content)

        return related
'''

print("\n" + "=" * 60)
print("第二部分：上下文服务")
print("=" * 60)
print(CONTEXT_SERVICE)


# ==================== 代码分析器 ====================

CODE_ANALYZER = '''
# app/services/code_analyzer.py
from tree_sitter_languages import get_language, get_parser
from typing import List, Dict, Optional

class CodeAnalyzer:
    """代码分析器 - 使用 tree-sitter"""

    SUPPORTED_LANGUAGES = {
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "java": "java",
        "go": "go",
        "rust": "rust",
    }

    def __init__(self):
        self.parsers = {}
        self.languages = {}

    def _get_parser(self, language: str):
        """获取解析器"""
        if language not in self.parsers:
            lang_id = self.SUPPORTED_LANGUAGES.get(language, language)
            self.parsers[language] = get_parser(lang_id)
            self.languages[language] = get_language(lang_id)
        return self.parsers[language], self.languages[language]

    def parse(self, code: str, language: str):
        """解析代码"""
        parser, _ = self._get_parser(language)
        return parser.parse(bytes(code, "utf8"))

    def get_functions(self, code: str, language: str = "python") -> List[Dict]:
        """提取函数定义"""
        parser, lang = self._get_parser(language)
        tree = parser.parse(bytes(code, "utf8"))

        # Python 函数查询
        if language == "python":
            query = lang.query("""
                (function_definition
                    name: (identifier) @func_name
                    parameters: (parameters) @params
                ) @func
            """)
        elif language in ["javascript", "typescript"]:
            query = lang.query("""
                (function_declaration
                    name: (identifier) @func_name
                    parameters: (formal_parameters) @params
                ) @func
            """)
        else:
            return []

        captures = query.captures(tree.root_node)
        functions = []
        for node, name in captures:
            if name == "func":
                functions.append({
                    "name": self._get_text(node, code),
                    "start_line": node.start_point[0],
                    "end_line": node.end_point[0],
                })
        return functions

    def get_imports(self, code: str, language: str = "python") -> List[str]:
        """提取导入语句"""
        parser, lang = self._get_parser(language)
        tree = parser.parse(bytes(code, "utf8"))

        imports = []
        if language == "python":
            query = lang.query("""
                (import_statement) @import
                (import_from_statement) @import_from
            """)
            for node, _ in query.captures(tree.root_node):
                imports.append(self._get_text(node, code))

        return imports

    def get_cursor_context(
        self,
        code: str,
        line: int,
        column: int,
        language: str = "python"
    ) -> Dict:
        """获取光标位置上下文"""
        parser, _ = self._get_parser(language)
        tree = parser.parse(bytes(code, "utf8"))

        point = (line, column)
        node = tree.root_node.descendant_for_point_range(point, point)

        # 查找父级函数和类
        parent_func = None
        parent_class = None
        current = node

        while current:
            if current.type in ["function_definition", "function_declaration"]:
                parent_func = self._get_text(current, code)
            elif current.type in ["class_definition", "class_declaration"]:
                parent_class = self._get_text(current, code)
            current = current.parent

        return {
            "node_type": node.type if node else None,
            "parent_function": parent_func,
            "parent_class": parent_class,
        }

    def _get_text(self, node, code: str) -> str:
        """获取节点文本"""
        return code[node.start_byte:node.end_byte]
'''

print("\n" + "=" * 60)
print("第三部分：代码分析器")
print("=" * 60)
print(CODE_ANALYZER)


# ==================== LLM 服务 ====================

LLM_SERVICE = '''
# app/services/llm_service.py
import google.generativeai as genai
from typing import AsyncGenerator
from app.config import get_settings

settings = get_settings()

class LLMService:
    """LLM 调用服务"""

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def complete(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = 500,
        temperature: float = 0.2,
        stop: list = None
    ) -> str:
        """常规补全"""
        response = await self.model.generate_content_async(prompt)
        return response.text

    async def stream_complete(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """流式补全"""
        response = self.model.generate_content(
            prompt,
            stream=True
        )
        
        for chunk in response:
            if hasattr(chunk, 'text'):
                yield chunk.text
'''

print("\n" + "=" * 60)
print("第四部分：LLM 服务")
print("=" * 60)
print(LLM_SERVICE)


# ==================== 补全服务 ====================

COMPLETION_SERVICE = '''
# app/services/completion_service.py
from app.services.context_service import ContextService, CodeContext
from app.services.llm_service import LLMService

class CompletionService:
    """代码补全服务"""

    PROMPT_TEMPLATE = """# 代码补全任务
语言: {language}

## 当前文件上下文
```{language}
{file_context}
```

## 补全位置
请补全 <CURSOR> 位置的代码：

```{language}
{prefix}<CURSOR>{suffix}
```

## 要求
- 只输出需要插入的代码，不要包含已有代码
- 保持代码风格一致
- 考虑上下文的变量和函数命名
- 代码应该语法正确且可执行

补全代码："""

    def __init__(self, context_service: ContextService, llm_service: LLMService):
        self.context_service = context_service
        self.llm_service = llm_service

    async def complete(
        self,
        file_path: str,
        file_content: str,
        cursor_line: int,
        cursor_column: int,
        language: str = "python"
    ) -> str:
        """执行代码补全"""
        # 1. 构建上下文
        context = await self.context_service.build_context(
            file_path, file_content, cursor_line, cursor_column, language
        )

        # 2. 截取相关上下文（避免超出 token 限制）
        prefix = context.prefix[-2000:] if len(context.prefix) > 2000 else context.prefix
        suffix = context.suffix[:500] if len(context.suffix) > 500 else context.suffix

        # 3. 构建 prompt
        prompt = self.PROMPT_TEMPLATE.format(
            language=language,
            file_context=self._get_file_context(context),
            prefix=prefix,
            suffix=suffix
        )

        # 4. 调用 LLM
        completion = await self.llm_service.complete(
            prompt=prompt,
            temperature=0.2,
            max_tokens=200,
            stop=["```", "\\n\\n"]
        )

        return completion.strip()

    def _get_file_context(self, context: CodeContext) -> str:
        """获取文件上下文摘要"""
        parts = []

        # 导入语句
        if context.imports:
            parts.append("# Imports")
            parts.extend(context.imports[:10])

        # 当前函数/类
        if context.current_function:
            parts.append(f"\\n# In function: {context.current_function}")
        if context.current_class:
            parts.append(f"# In class: {context.current_class}")

        return "\\n".join(parts)
'''

print("\n" + "=" * 60)
print("第五部分：补全服务")
print("=" * 60)
print(COMPLETION_SERVICE)


# ==================== API 接口 ====================

API_CODE = '''
# app/api/completion.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.completion_service import CompletionService
from app.dependencies import get_completion_service

router = APIRouter(prefix="/completion", tags=["completion"])

class CompletionRequest(BaseModel):
    file_path: str
    file_content: str
    cursor_line: int
    cursor_column: int
    language: str = "python"

class CompletionResponse(BaseModel):
    completion: str
    confidence: Optional[float] = None

@router.post("", response_model=CompletionResponse)
async def get_completion(
    request: CompletionRequest,
    service: CompletionService = Depends(get_completion_service)
):
    """获取代码补全"""
    completion = await service.complete(
        file_path=request.file_path,
        file_content=request.file_content,
        cursor_line=request.cursor_line,
        cursor_column=request.cursor_column,
        language=request.language
    )
    return CompletionResponse(completion=completion)


# app/api/generation.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/generate", tags=["generation"])

class GenerationRequest(BaseModel):
    instruction: str
    context: str = ""
    language: str = "python"

@router.post("/stream")
async def generate_code_stream(request: GenerationRequest):
    """流式生成代码"""
    async def generate():
        prompt = f"""根据以下指令生成 {request.language} 代码：

指令：{request.instruction}

上下文：
{request.context}

生成代码："""

        async for chunk in llm_service.stream_complete(prompt):
            yield f"data: {chunk}\\n\\n"
        yield "data: [DONE]\\n\\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# app/api/review.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/review", tags=["review"])

class ReviewRequest(BaseModel):
    code: str
    language: str = "python"

class ReviewItem(BaseModel):
    severity: str  # "error", "warning", "info"
    line: int
    message: str
    suggestion: str

class ReviewResponse(BaseModel):
    issues: List[ReviewItem]
    summary: str
    score: float

@router.post("", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    """代码评审"""
    prompt = f"""请评审以下 {request.language} 代码：

```{request.language}
{request.code}
```

请以 JSON 格式返回：
{{
    "issues": [
        {{"severity": "error/warning/info", "line": 行号, "message": "问题描述", "suggestion": "修复建议"}}
    ],
    "summary": "总体评价",
    "score": 0-100的评分
}}"""

    result = await llm_service.complete(prompt)
    import json
    return ReviewResponse(**json.loads(result))
'''

print("\n" + "=" * 60)
print("第六部分：API 接口")
print("=" * 60)
print(API_CODE)


# ==================== VSCode 插件 ====================

VSCODE_EXTENSION = """
// extensions/vscode/src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    // 注册补全提供者
    const provider = vscode.languages.registerCompletionItemProvider(
        ['python', 'javascript', 'typescript'],
        new AICompletionProvider(),
        '.'  // 触发字符
    );

    // 注册命令
    const explainCmd = vscode.commands.registerCommand(
        'codeAssistant.explain',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;

            const selection = editor.selection;
            const code = editor.document.getText(selection);

            const explanation = await callAPI('/explain', { code });
            vscode.window.showInformationMessage(explanation);
        }
    );

    context.subscriptions.push(provider, explainCmd);
}

class AICompletionProvider implements vscode.CompletionItemProvider {
    async provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position
    ): Promise<vscode.CompletionItem[]> {

        const response = await callAPI('/completion', {
            file_path: document.fileName,
            file_content: document.getText(),
            cursor_line: position.line,
            cursor_column: position.character,
            language: document.languageId
        });

        const item = new vscode.CompletionItem(
            response.completion,
            vscode.CompletionItemKind.Snippet
        );
        item.insertText = response.completion;

        return [item];
    }
}

async function callAPI(endpoint: string, data: any): Promise<any> {
    const config = vscode.workspace.getConfiguration('codeAssistant');
    const baseUrl = config.get('apiUrl', 'http://localhost:8000');

    const response = await fetch(`${baseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    return response.json();
}
"""

print("\n" + "=" * 60)
print("第七部分：VSCode 插件")
print("=" * 60)
print(VSCODE_EXTENSION)


print("\n" + "=" * 60)
print("🎉 Phase 12 课程完成！")
print("=" * 60)
print("""
恭喜完成所有综合项目学习！

回顾已学习的项目：
1. 企业级知识库系统 - RAG + 权限管理
2. AI 客服系统 - 对话管理 + 人工接入
3. 代码助手 - 代码分析 + LLM 生成

下一步建议：
- 选择一个项目深入实现
- 加入更多高级功能
- 部署到生产环境
""")
