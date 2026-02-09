"""
企业级知识库系统 - 架构设计
========================

学习目标：
    1. 理解企业级知识库的架构设计
    2. 掌握技术选型和系统分层
    3. 设计可扩展的 RAG 系统

项目概述：
    构建一个支持多用户、多文档格式、高并发的企业级知识库系统，
    支持智能问答、权限管理、数据分析等功能。

技术栈：
    - 后端：FastAPI + LangChain
    - 向量库：Milvus / Qdrant
    - 数据库：PostgreSQL + Redis
    - LLM：GPT-4 / Claude / 开源模型
"""


# ==================== 第一部分：需求分析 ====================


def requirements():
    """需求分析"""
    print("=" * 60)
    print("第一部分：需求分析")
    print("=" * 60)

    print("""
    📌 核心功能需求：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 文档管理                                            │
    │    - 多格式支持：PDF, Word, Excel, Markdown, HTML      │
    │    - 批量上传和处理                                    │
    │    - 文档版本管理                                      │
    │                                                        │
    │ 2. 智能问答                                            │
    │    - 基于 RAG 的精准问答                               │
    │    - 多轮对话支持                                      │
    │    - 引用溯源                                          │
    │                                                        │
    │ 3. 权限管理                                            │
    │    - 用户认证与授权                                    │
    │    - 文档级别权限控制                                  │
    │    - 知识库隔离                                        │
    │                                                        │
    │ 4. 运营管理                                            │
    │    - 使用统计和分析                                    │
    │    - 问答质量监控                                      │
    │    - 成本追踪                                          │
    └─────────────────────────────────────────────────────────┘

    📌 非功能需求：
    - 并发支持：100+ QPS
    - 响应时间：< 3s
    - 可用性：99.9%
    - 数据安全：企业级加密
    """)


# ==================== 第二部分：架构设计 ====================


def architecture():
    """架构设计"""
    print("\n" + "=" * 60)
    print("第二部分：系统架构设计")
    print("=" * 60)

    print("""
    📌 整体架构：
    ┌─────────────────────────────────────────────────────────────┐
    │                        前端层                               │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
    │  │  Web UI  │ │  移动端  │ │   API    │ │  插件    │       │
    │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
    └───────┼────────────┼────────────┼────────────┼─────────────┘
            │            │            │            │
    ┌───────┴────────────┴────────────┴────────────┴─────────────┐
    │                      API 网关层                             │
    │  ┌────────────────────────────────────────────────────┐    │
    │  │  认证/授权  │  限流  │  负载均衡  │  日志  │  监控  │    │
    │  └────────────────────────────────────────────────────┘    │
    └───────────────────────────┬─────────────────────────────────┘
                                │
    ┌───────────────────────────┴─────────────────────────────────┐
    │                       服务层                                │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
    │  │  问答服务  │ │  文档服务  │ │  用户服务  │              │
    │  └────────────┘ └────────────┘ └────────────┘              │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
    │  │ 检索服务   │ │ 向量服务   │ │ 分析服务   │              │
    │  └────────────┘ └────────────┘ └────────────┘              │
    └───────────────────────────┬─────────────────────────────────┘
                                │
    ┌───────────────────────────┴─────────────────────────────────┐
    │                       存储层                                │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
    │  │PostgreSQL│ │  Redis   │ │  Milvus  │ │   OSS    │       │
    │  │ (元数据) │ │  (缓存)  │ │ (向量库) │ │ (文件)   │       │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
    └─────────────────────────────────────────────────────────────┘

    📌 核心服务职责：
    ┌────────────┬────────────────────────────────────────────┐
    │ 问答服务   │ RAG 检索、LLM 生成、对话管理             │
    │ 文档服务   │ 文档解析、分块、索引管理                 │
    │ 检索服务   │ 向量检索、混合检索、重排序               │
    │ 向量服务   │ Embedding 生成、向量库管理               │
    │ 用户服务   │ 认证授权、权限管理                       │
    │ 分析服务   │ 统计分析、报表生成                       │
    └────────────┴────────────────────────────────────────────┘
    """)


# ==================== 第三部分：技术选型 ====================


def tech_stack():
    """技术选型"""
    print("\n" + "=" * 60)
    print("第三部分：技术选型")
    print("=" * 60)

    print("""
    📌 技术栈选择：
    ┌─────────────┬────────────────┬────────────────────────────┐
    │   层级      │    技术选型    │         理由               │
    ├─────────────┼────────────────┼────────────────────────────┤
    │ Web框架     │ FastAPI        │ 高性能、异步、OpenAPI      │
    │ LLM框架     │ LangChain      │ 生态丰富、抽象完善         │
    │ 向量数据库  │ Milvus/Qdrant  │ 高性能、可扩展             │
    │ 关系数据库  │ PostgreSQL     │ 稳定可靠、功能丰富         │
    │ 缓存        │ Redis          │ 高性能、多数据结构         │
    │ 消息队列    │ Celery+Redis   │ 异步任务处理               │
    │ 对象存储    │ MinIO/S3       │ 文件存储                   │
    │ 容器化      │ Docker+K8s     │ 部署运维标准化             │
    │ 监控        │ Prometheus     │ 指标采集和告警             │
    └─────────────┴────────────────┴────────────────────────────┘

    📌 LLM 选型策略：
    ┌────────────────┬─────────────────────────────────────────┐
    │ 场景           │ 推荐模型                                │
    ├────────────────┼─────────────────────────────────────────┤
    │ 复杂问答       │ GPT-4o / Claude 3.5                    │
    │ 简单问答       │ GPT-4o-mini / Claude 3 Haiku           │
    │ Embedding      │ text-embedding-3-small                  │
    │ 私有化部署     │ Qwen2 / GLM-4 / Llama 3                │
    └────────────────┴─────────────────────────────────────────┘
    """)


# ==================== 第四部分：RAG 流程设计 ====================


def rag_design():
    """RAG 流程设计"""
    print("\n" + "=" * 60)
    print("第四部分：RAG 流程设计")
    print("=" * 60)

    print("""
    📌 文档处理流程：
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │ 文档   │ -> │ 解析   │ -> │ 分块   │ -> │ 向量化 │
    │ 上传   │    │ 提取   │    │ 策略   │    │ 存储   │
    └────────┘    └────────┘    └────────┘    └────────┘

    📌 问答流程：
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │ 用户   │ -> │ 查询   │ -> │ 向量   │ -> │ 重排序 │ -> │ LLM    │
    │ 提问   │    │ 改写   │    │ 检索   │    │ 过滤   │    │ 生成   │
    └────────┘    └────────┘    └────────┘    └────────┘    └────────┘

    📌 分块策略：
    - 默认：RecursiveCharacterTextSplitter
    - chunk_size: 500-1000
    - overlap: 100-200
    - 保留元数据：标题、来源、页码

    📌 检索策略：
    - 混合检索：向量 + 关键词
    - top_k: 10-20
    - Reranker 重排序
    - 相似度阈值过滤
    """)


# ==================== 第五部分：数据库设计 ====================


def database_design():
    """数据库设计"""
    print("\n" + "=" * 60)
    print("第五部分：数据库设计")
    print("=" * 60)

    code = '''
# PostgreSQL 表结构设计

"""
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识库表
CREATE TABLE knowledge_bases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文档表
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kb_id UUID REFERENCES knowledge_bases(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    file_path VARCHAR(500),
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    kb_id UUID REFERENCES knowledge_bases(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
'''
    print(code)


# ==================== 第六部分：API 设计 ====================


def api_design():
    """API 设计"""
    print("\n" + "=" * 60)
    print("第六部分：API 设计")
    print("=" * 60)

    print("""
    📌 核心 API 端点：

    # 知识库管理
    POST   /api/v1/knowledge-bases          创建知识库
    GET    /api/v1/knowledge-bases          获取知识库列表
    GET    /api/v1/knowledge-bases/{id}     获取知识库详情
    DELETE /api/v1/knowledge-bases/{id}     删除知识库

    # 文档管理
    POST   /api/v1/documents/upload         上传文档
    GET    /api/v1/documents                获取文档列表
    DELETE /api/v1/documents/{id}           删除文档
    POST   /api/v1/documents/{id}/reindex   重新索引

    # 问答
    POST   /api/v1/chat                     发送消息（支持流式）
    GET    /api/v1/conversations            获取对话历史
    DELETE /api/v1/conversations/{id}       删除对话

    # 用户管理
    POST   /api/v1/auth/login               登录
    POST   /api/v1/auth/register            注册
    GET    /api/v1/users/me                 当前用户信息
    """)


# ==================== 第七部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：设计一个多租户知识库系统的权限模型

        ✅ 参考答案：
        ```python
        from enum import Enum
        from typing import List, Optional
        from pydantic import BaseModel
        
        class Permission(str, Enum):
            '''权限类型'''
            READ = "read"           # 查看文档和问答
            WRITE = "write"         # 上传/编辑文档
            DELETE = "delete"       # 删除文档
            MANAGE = "manage"       # 管理成员权限
            ADMIN = "admin"         # 完全控制
        
        class Role(str, Enum):
            '''预定义角色'''
            VIEWER = "viewer"       # 只读用户
            EDITOR = "editor"       # 可编辑
            ADMIN = "admin"         # 管理员
            OWNER = "owner"         # 所有者
        
        # 角色-权限映射
        ROLE_PERMISSIONS = {
            Role.VIEWER: [Permission.READ],
            Role.EDITOR: [Permission.READ, Permission.WRITE],
            Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.MANAGE],
            Role.OWNER: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.MANAGE, Permission.ADMIN],
        }
        
        class KnowledgeBaseAccess(BaseModel):
            '''知识库访问记录'''
            user_id: str
            kb_id: str
            role: Role
            granted_by: str
            expires_at: Optional[str] = None
        
        class PermissionService:
            '''权限服务'''
            
            async def check_permission(
                self, 
                user_id: str, 
                kb_id: str, 
                required: Permission
            ) -> bool:
                '''检查用户权限'''
                access = await self.get_access(user_id, kb_id)
                if not access:
                    return False
                
                allowed = ROLE_PERMISSIONS.get(access.role, [])
                return required in allowed
            
            async def grant_access(
                self,
                granter_id: str,
                target_user_id: str,
                kb_id: str,
                role: Role
            ) -> bool:
                '''授予访问权限'''
                # 检查授予者是否有 MANAGE 权限
                if not await self.check_permission(granter_id, kb_id, Permission.MANAGE):
                    raise PermissionError("无权授予访问权限")
                
                # 不能授予比自己更高的权限
                granter_access = await self.get_access(granter_id, kb_id)
                if self._role_level(role) > self._role_level(granter_access.role):
                    raise PermissionError("不能授予比自己更高的权限")
                
                # 保存访问记录
                await self.save_access(KnowledgeBaseAccess(
                    user_id=target_user_id,
                    kb_id=kb_id,
                    role=role,
                    granted_by=granter_id
                ))
                return True
        ```
    
    练习 2：设计知识库的分块策略配置

        ✅ 参考答案：
        ```python
        from pydantic import BaseModel, Field
        from enum import Enum
        
        class ChunkStrategy(str, Enum):
            '''分块策略'''
            RECURSIVE = "recursive"         # 递归字符分割
            SEMANTIC = "semantic"           # 语义分割
            MARKDOWN = "markdown"           # Markdown 结构分割
            CODE = "code"                   # 代码分割
        
        class ChunkConfig(BaseModel):
            '''分块配置'''
            strategy: ChunkStrategy = ChunkStrategy.RECURSIVE
            chunk_size: int = Field(default=500, ge=100, le=2000)
            chunk_overlap: int = Field(default=100, ge=0, le=500)
            
            # 语义分割特有配置
            semantic_threshold: float = Field(default=0.7, ge=0.5, le=0.95)
            
            # 代码分割特有配置
            code_language: str = "python"
            split_by_function: bool = True
        
        # 预设配置
        CHUNK_PRESETS = {
            "default": ChunkConfig(),
            "technical_docs": ChunkConfig(
                strategy=ChunkStrategy.MARKDOWN,
                chunk_size=800,
                chunk_overlap=150
            ),
            "code_repo": ChunkConfig(
                strategy=ChunkStrategy.CODE,
                chunk_size=1000,
                chunk_overlap=200,
                split_by_function=True
            ),
            "qa_pairs": ChunkConfig(
                strategy=ChunkStrategy.SEMANTIC,
                chunk_size=300,
                chunk_overlap=50,
                semantic_threshold=0.8
            ),
        }
        
        def get_chunk_config(
            doc_type: str, 
            custom_config: dict = None
        ) -> ChunkConfig:
            '''获取分块配置'''
            # 根据文档类型选择预设
            presets_map = {
                ".md": "technical_docs",
                ".py": "code_repo",
                ".js": "code_repo",
                ".pdf": "default",
            }
            preset_name = presets_map.get(doc_type, "default")
            config = CHUNK_PRESETS[preset_name].copy()
            
            # 应用自定义配置
            if custom_config:
                for key, value in custom_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            
            return config
        ```

    思考题：向量数据库和关系数据库如何配合使用？

        ✅ 答：
        1. 职责分离：
           - 向量数据库：存储 embedding、语义检索
           - 关系数据库：存储元数据、权限、关联关系
        
        2. 数据同步：
           - 文档上传：先存 PostgreSQL，再存 Milvus
           - 文档删除：先删 Milvus，再删 PostgreSQL
           - 使用事务保证一致性
        
        3. 查询协作：
           - 先从向量库检索相似文档 ID
           - 用 ID 查询 PostgreSQL 获取元数据和权限
           - 过滤无权访问的结果
        
        4. 典型架构：
           ```
           用户查询 -> 权限校验(PG) -> 向量检索(Milvus) 
                    -> 元数据填充(PG) -> 返回结果
           ```
        
        5. 索引策略：
           - PostgreSQL: 常规查询索引 (B-tree)
           - Milvus/Qdrant: ANN 索引 (HNSW/IVF_FLAT)
    """)


def main():
    requirements()
    architecture()
    tech_stack()
    rag_design()
    database_design()
    api_design()
    exercises()


if __name__ == "__main__":
    main()
