#!/usr/bin/env python3
"""
MediMind - 数据库初始化脚本

创建数据库表并加载初始数据。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db import init_database, get_database
from src.utils import log, setup_logger


def main():
    """主函数"""
    setup_logger(level="INFO")
    
    log.info("=" * 50)
    log.info("MediMind 数据库初始化脚本")
    log.info("=" * 50)
    
    try:
        # 初始化数据库
        db = init_database()
        
        log.info("✅ 数据库初始化完成！")
        log.info("=" * 50)
        
        # 显示表信息
        from src.models.base import Base
        tables = Base.metadata.tables.keys()
        log.info(f"已创建表: {', '.join(tables)}")
        
    except Exception as e:
        log.error(f"数据库初始化失败: {e}")
        raise


if __name__ == "__main__":
    main()
