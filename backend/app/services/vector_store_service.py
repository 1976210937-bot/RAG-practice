"""
向量存储服务模块
封装Chroma向量数据库的操作
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional, Dict, Any
from langchain_chroma import Chroma
from app.config import settings
from app.services.embedding_service import embedding_service


class VectorStoreService:
    """
    Chroma向量存储服务类
    提供文档的向量存储、检索、删除等功能
    """
    
    def __init__(self):
        """初始化向量存储服务"""
        # 初始化Chroma客户端
        self._client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
        
        # 获取或创建集合
        self._collection = self._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "企业知识库向量集合"}
        )
        
        # LangChain Chroma 实例（用于检索）
        self._langchain_chroma = Chroma(
            client=self._client,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embedding_service
        )
    
    @property
    def langchain_chroma(self) -> Chroma:
        """获取LangChain兼容的Chroma实例"""
        return self._langchain_chroma
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        向向量库中添加文档
        
        Args:
            texts: 文档文本列表
            metadatas: 元数据列表（可选）
            ids: 文档ID列表（可选，不传则自动生成）
            
        Returns:
            添加的文档ID列表
        """
        # 生成嵌入向量
        embeddings = embedding_service.embed_documents(texts)
        
        # 添加到集合
        result = self._collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids if ids else result.get("ids", [])
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件
            
        Returns:
            搜索结果列表，每个结果包含document、metadata、distance等
        """
        # 生成查询向量
        query_embedding = embedding_service.embed_query(query)
        
        # 执行搜索
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter
        )
        
        # 格式化结果
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                    "id": results["ids"][0][i] if results["ids"] else ""
                })
        
        return formatted_results
    
    def delete_by_document_id(self, document_id: int) -> int:
        """
        根据文档ID删除所有相关向量
        
        Args:
            document_id: 文档ID
            
        Returns:
            删除的向量数量
        """
        # 查询该文档的所有向量
        results = self._collection.get(
            where={"document_id": document_id}
        )
        
        if results["ids"]:
            self._collection.delete(ids=results["ids"])
            return len(results["ids"])
        
        return 0
    
    def count(self) -> int:
        """获取向量库中的向量总数"""
        return self._collection.count()
    
    def get_document_chunk_count(self, document_id: int) -> int:
        """
        获取指定文档的分块数量
        
        Args:
            document_id: 文档ID
            
        Returns:
            分块数量
        """
        results = self._collection.get(
            where={"document_id": document_id}
        )
        return len(results["ids"]) if results["ids"] else 0


# 全局向量存储服务实例
vector_store_service = VectorStoreService()
