"""
系统配置模块
从环境变量或.env文件中读取配置信息
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """系统配置类，统一管理所有配置项"""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./rag_knowledge.db"
    
    # JWT 认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # DeepSeek LLM 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 阿里通义千问 Embedding 配置
    DASHSCOPE_API_KEY: str = ""
    QWEN_EMBEDDING_MODEL: str = "qwen3-embedding"
    
    # Chroma 向量数据库配置
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "rag_knowledge"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
