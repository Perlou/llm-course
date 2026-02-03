"""
MediMind - 数据库连接管理

支持 PostgreSQL 和 SQLite 数据库。
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.utils import get_settings, log
from src.models.base import Base


class Database:
    """数据库管理器"""

    def __init__(self, database_url: str = None):
        settings = get_settings()
        self.database_url = database_url or settings.database_url
        
        # 根据数据库类型配置引擎参数
        if self.database_url.startswith("sqlite"):
            # SQLite 配置
            engine_kwargs = {
                "connect_args": {"check_same_thread": False},
            }
        else:
            # PostgreSQL 配置
            engine_kwargs = {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_pre_ping": True,
            }
        
        self.engine = create_engine(
            self.database_url,
            echo=settings.debug,
            **engine_kwargs,
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        
        log.info(f"数据库已配置: {self._safe_url()}")

    def _safe_url(self) -> str:
        """返回隐藏密码的 URL"""
        if "@" in self.database_url:
            parts = self.database_url.split("@")
            prefix = parts[0].rsplit(":", 1)[0]
            suffix = parts[1]
            return f"{prefix}:***@{suffix}"
        return self.database_url

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)
        log.info("数据库表创建完成")

    def drop_tables(self):
        """删除所有表（危险操作）"""
        Base.metadata.drop_all(bind=self.engine)
        log.warning("数据库表已删除")

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        提供事务作用域的会话
        
        Usage:
            with db.session_scope() as session:
                session.add(obj)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# 全局数据库实例
_database: Database = None


def get_database() -> Database:
    """获取数据库单例"""
    global _database
    if _database is None:
        _database = Database()
    return _database


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 依赖注入用的数据库会话生成器
    
    Usage:
        @router.get("/items")
        async def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = get_database()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


def init_database():
    """初始化数据库（创建表）"""
    db = get_database()
    db.create_tables()
    return db
