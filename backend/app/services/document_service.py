"""
文档处理服务模块
负责文档加载、文本分割、向量化入库等处理
"""
import os
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models import Document
from app.database import SessionLocal
from app.services.vector_store_service import vector_store_service


class DocumentProcessor:
    """
    文档处理器类
    负责文档的文本提取、分块、向量化等处理
    """
    
    def __init__(self):
        """初始化文档处理器"""
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,        # 每个分块的大小（字符数）
            chunk_overlap=50,      # 分块之间的重叠大小
            length_function=len,
            separators=[
                "\n\n",  # 段落
                "\n",    # 行
                "。",    # 中文句号
                "！",    # 中文感叹号
                "？",    # 中文问号
                ". ",    # 英文句号
                "! ",    # 英文感叹号
                "? ",    # 英文问号
                " ",     # 空格
                "",      # 字符
            ]
        )
    
    def load_file_content(self, file_path: str, file_type: str) -> str:
        """
        从文件中加载文本内容
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            提取的文本内容
        """
        if not os.path.exists(file_path):
            return ""
        
        # 文本类文件直接读取
        text_extensions = ['.txt', '.md', '.py', '.js', '.ts', '.html', '.css', 
                          '.json', '.csv', '.xml', '.yaml', '.yml', '.java', 
                          '.go', '.rs', '.c', '.cpp', '.h']
        
        ext = f".{file_type.lower()}" if not file_type.startswith('.') else file_type.lower()
        
        if ext in text_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        return f.read()
                except UnicodeDecodeError:
                    return ""
        
        return ""
    
    def split_text(self, text: str) -> List[str]:
        """
        将文本分割成多个块
        
        Args:
            text: 原始文本
            
        Returns:
            分割后的文本块列表
        """
        if not text.strip():
            return []
        
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    def process_document(self, document_id: int) -> Tuple[bool, str]:
        """
        处理文档：读取内容、分块、向量化入库
        
        Args:
            document_id: 文档ID
            
        Returns:
            (是否成功, 消息)
        """
        db = SessionLocal()
        try:
            # 获取文档
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                return False, "文档不存在"
            
            # 更新状态为处理中
            doc.status = "processing"
            db.commit()
            
            # 读取文件内容
            content = self.load_file_content(doc.file_path, doc.file_type or "")
            if not content:
                # 如果content字段已有内容，使用content字段
                if doc.content:
                    content = doc.content
                else:
                    doc.status = "failed"
                    db.commit()
                    return False, "无法提取文档内容"
            
            # 更新文档内容
            doc.content = content
            
            # 文本分块
            chunks = self.split_text(content)
            if not chunks:
                doc.status = "failed"
                db.commit()
                return False, "文档内容为空或分割失败"
            
            # 准备元数据
            metadatas = []
            ids = []
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    "document_id": doc.id,
                    "title": doc.title,
                    "file_name": doc.file_name or "",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source": doc.title
                })
                ids.append(f"doc_{doc.id}_chunk_{i}")
            
            # 向量化入库
            vector_store_service.add_documents(
                texts=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            # 更新文档状态
            doc.chunk_count = len(chunks)
            doc.status = "completed"
            db.commit()
            
            return True, f"处理成功，共生成{len(chunks)}个文本块"
            
        except Exception as e:
            # 更新状态为失败
            try:
                doc = db.query(Document).filter(Document.id == document_id).first()
                if doc:
                    doc.status = "failed"
                    db.commit()
            except:
                pass
            return False, f"处理失败: {str(e)}"
        finally:
            db.close()
    
    def delete_document_vectors(self, document_id: int) -> int:
        """
        删除文档的所有向量
        
        Args:
            document_id: 文档ID
            
        Returns:
            删除的向量数量
        """
        return vector_store_service.delete_by_document_id(document_id)


# 全局文档处理器实例
document_processor = DocumentProcessor()
