"""
Embedding服务模块
封装阿里通义千问Qwen3-Embedding嵌入模型，支持本地降级方案
"""
import random
from typing import List
from langchain_core.embeddings import Embeddings
from app.config import settings


class LocalEmbeddingService(Embeddings):
    """
    本地简易Embedding服务（降级方案）
    使用随机向量生成嵌入，用于演示和开发环境
    """
    
    def __init__(self, dimension: int = 1024):
        """初始化本地Embedding服务"""
        self.dimension = dimension
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        对文档列表生成嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        return [[random.random() * 2 - 1 for _ in range(self.dimension)] for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """
        对查询文本生成嵌入向量
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        return [random.random() * 2 - 1 for _ in range(self.dimension)]


class QwenEmbeddingService(Embeddings):
    """
    阿里通义千问Embedding服务类
    使用DashScopeEmbeddings调用qwen3-embedding模型
    """
    
    def __init__(self):
        """初始化Embedding服务"""
        self._embeddings = None
        self._local_embedding = LocalEmbeddingService(1024)
        self._use_local = False
        
        # 检查API Key是否配置
        if not settings.DASHSCOPE_API_KEY or settings.DASHSCOPE_API_KEY == 'your-dashscope-api-key-here':
            print("警告：未配置DashScope API Key，使用本地降级方案")
            self._use_local = True
            return
        
        # 尝试初始化DashScope Embedding
        try:
            from langchain_community.embeddings import DashScopeEmbeddings
            self._embeddings = DashScopeEmbeddings(
                model=settings.QWEN_EMBEDDING_MODEL,
                dashscope_api_key=settings.DASHSCOPE_API_KEY
            )
        except Exception as e:
            print(f"初始化DashScope Embedding失败，使用本地降级方案: {e}")
            self._use_local = True
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        对文档列表生成嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        if self._use_local or self._embeddings is None:
            return self._local_embedding.embed_documents(texts)
        
        try:
            return self._embeddings.embed_documents(texts)
        except Exception as e:
            print(f"调用DashScope Embedding失败，降级使用本地方案: {e}")
            return self._local_embedding.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        对查询文本生成嵌入向量
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        if self._use_local or self._embeddings is None:
            return self._local_embedding.embed_query(text)
        
        try:
            return self._embeddings.embed_query(text)
        except Exception as e:
            print(f"调用DashScope Embedding失败，降级使用本地方案: {e}")
            return self._local_embedding.embed_query(text)


# 全局Embedding服务实例
embedding_service = QwenEmbeddingService()
