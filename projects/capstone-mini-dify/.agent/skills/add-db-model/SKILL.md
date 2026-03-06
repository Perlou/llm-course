---
name: add-db-model
description: 为 Mini-Dify 添加 SQLAlchemy 数据模型和 Alembic 迁移
---

# 添加数据模型技能

此技能用于为 Mini-Dify 添加新的 SQLAlchemy 数据模型并生成 Alembic 迁移。

## 数据模型目录

```
backend/app/models/
├── __init__.py          # 导出所有模型
├── base.py              # 基类 (Base, 公共字段)
├── provider.py          # 供应商模型
├── prompt.py            # Prompt 模型
├── dataset.py           # 知识库模型
├── agent.py             # Agent 模型
├── workflow.py          # 工作流模型
├── app.py               # 应用模型
└── log.py               # 日志模型
```

## 步骤

### 1. 定义 Base 基类（如尚未创建）

```python
# app/models/base.py
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """公共时间戳字段"""
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
        nullable=False
    )


class UUIDPrimaryKeyMixin:
    """UUID 主键"""
    id = Column(
        UUID, primary_key=True,
        server_default=text("gen_random_uuid()")
    )
```

### 2. 创建新模型

```python
# app/models/new_model.py
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class NewModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "new_models"

    # 基本字段
    name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)

    # JSONB 字段（PostgreSQL 特性）
    config = Column(JSONB, default=dict, nullable=False)

    # 数组字段（PostgreSQL 特性）
    tags = Column(ARRAY(String), default=list)

    # 枚举字段
    status = Column(String(20), default="draft", nullable=False)

    # 外键
    parent_id = Column(UUID, ForeignKey("parents.id"), nullable=True)

    # 布尔
    is_active = Column(Boolean, default=True)

    # 关系
    parent = relationship("Parent", back_populates="children")
    items = relationship("Item", back_populates="new_model", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NewModel(id={self.id}, name={self.name})>"
```

### 3. 在 `__init__.py` 注册

```python
# app/models/__init__.py
from .base import Base
from .provider import Provider
from .new_model import NewModel  # 新增
# ... 其他模型

__all__ = ["Base", "Provider", "NewModel"]
```

### 4. 生成 Alembic 迁移

```bash
cd backend

# 自动生成迁移
alembic revision --autogenerate -m "add new_models table"

# 检查生成的迁移文件
# alembic/versions/xxx_add_new_models_table.py

# 执行迁移
alembic upgrade head

# 如需回退
alembic downgrade -1
```

## PostgreSQL 字段类型映射

| Python / SQLAlchemy        | PostgreSQL         | 使用场景       |
| -------------------------- | ------------------ | -------------- |
| `UUID`                     | `uuid`             | 主键、外键     |
| `String(n)`                | `varchar(n)`       | 短文本         |
| `String` (无长度)          | `text`             | 长文本         |
| `JSONB`                    | `jsonb`            | 可变结构数据   |
| `ARRAY(String)`            | `text[]`           | 标签等多值     |
| `ARRAY(UUID)`              | `uuid[]`           | UUID 数组      |
| `Boolean`                  | `boolean`          | 布尔值         |
| `Integer`                  | `integer`          | 整数           |
| `Float`                    | `double precision` | 浮点（如温度） |
| `TIMESTAMP(timezone=True)` | `timestamptz`      | 时间戳         |

## 常用索引

```python
from sqlalchemy import Index

# 单列索引
Index("idx_new_model_status", NewModel.status)

# 复合索引
Index("idx_new_model_parent_created", NewModel.parent_id, NewModel.created_at.desc())

# JSONB GIN 索引
Index("idx_new_model_config", NewModel.config, postgresql_using="gin")

# 唯一约束
Index("idx_new_model_name_unique", NewModel.name, unique=True)
```

## 关联表模式

```python
# 多对多关联表
from sqlalchemy import Table

agent_tools = Table(
    "agent_tools", Base.metadata,
    Column("agent_id", UUID, ForeignKey("agents.id"), primary_key=True),
    Column("tool_id", UUID, ForeignKey("tools.id"), primary_key=True),
)
```

## 数据库异步操作示例

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def create_item(db: AsyncSession, data: dict) -> NewModel:
    item = NewModel(**data)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_items(db: AsyncSession, page=1, size=20) -> tuple[list, int]:
    offset = (page - 1) * size
    result = await db.execute(
        select(NewModel).offset(offset).limit(size).order_by(NewModel.created_at.desc())
    )
    items = result.scalars().all()
    total = await db.scalar(select(func.count(NewModel.id)))
    return items, total


async def get_item(db: AsyncSession, item_id) -> NewModel | None:
    return await db.get(NewModel, item_id)


async def delete_item(db: AsyncSession, item_id):
    item = await db.get(NewModel, item_id)
    if item:
        await db.delete(item)
        await db.commit()
```

## 注意事项

1. **UUID 主键**: 所有表使用 PostgreSQL 原生 UUID
2. **JSONB**: 可变结构数据首选 JSONB（支持索引查询）
3. **时区**: 时间字段始终使用 `TIMESTAMPTZ`
4. **迁移**: 修改模型后必须生成并执行 Alembic 迁移
5. **级联删除**: 父子关系使用 `cascade="all, delete-orphan"`
