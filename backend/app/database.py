"""
数据库连接与会话管理模块
提供SQLAlchemy的数据库引擎、会话工厂和基类
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 创建数据库引擎，SQLite需要加上check_same_thread=False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库模型基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖生成器
    使用完毕后自动关闭会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
