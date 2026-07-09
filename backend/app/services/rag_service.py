"""
RAG问答服务模块
实现基于检索增强生成的问答功能
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.services.vector_store_service import vector_store_service
from app.services.llm_service import llm_service, LocalLLMService

# 配置日志
logger = logging.getLogger(__name__)

# RAG 系统提示词模板
RAG_SYSTEM_PROMPT = """你是一个专业的企业知识库问答助手。请根据以下提供的参考资料来回答用户的问题。

【参考资料】
{context}

【回答规则】
1. 请基于参考资料中的信息来回答问题，不要编造资料中没有的内容
2. 如果参考资料中没有相关信息，请明确告知用户"抱歉，知识库中暂未找到相关信息"
3. 回答要准确、简洁、条理清晰
4. 对于有多个要点的问题，请使用序号列出
5. 引用资料时请注明来源文档标题

现在请回答用户的问题：
{question}
"""


class RAGService:
    """
    RAG问答服务类
    实现检索增强生成的完整问答流程
    """
    
    def __init__(self):
        """初始化RAG服务"""
        self.llm = llm_service.get_llm()
        self.retriever = vector_store_service.langchain_chroma.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 2}
        )
        
        # 创建提示词模板
        self.prompt = ChatPromptTemplate.from_template(RAG_SYSTEM_PROMPT)
        
        # 判断是否使用本地LLM
        self._use_local_llm = isinstance(self.llm, LocalLLMService)
        
        # 创建RAG链（仅当使用真实LLM时）
        if not self._use_local_llm:
            try:
                self.rag_chain = (
                    {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
                    | self.prompt
                    | self.llm
                    | StrOutputParser()
                )
            except Exception as e:
                print(f"创建RAG链失败，将使用简化模式: {e}")
                self._use_local_llm = True
        else:
            self.rag_chain = None
    
    def _format_docs(self, docs) -> str:
        """
        格式化检索到的文档为字符串
        
        Args:
            docs: 检索到的文档列表
            
        Returns:
            格式化后的文档内容字符串
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get("title", "未知文档")
            source = doc.metadata.get("source", "")
            formatted.append(
                f"[资料{i}] 标题：{title}\n"
                f"内容：{doc.page_content}"
            )
        return "\n\n".join(formatted)
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        使用RAG回答用户问题
        
        Args:
            question: 用户问题
            
        Returns:
            包含回答和引用来源的字典
            {
                "answer": "回答内容",
                "sources": [
                    {
                        "document_id": 文档ID,
                        "title": "文档标题",
                        "content": "相关内容",
                        "score": 相似度分数
                    }
                ]
            }
        """
        # 第一步：检索相关文档
        search_results = vector_store_service.similarity_search(question, k=4)
        
        # 第二步：构造上下文
        context_parts = []
        sources = []
        for i, result in enumerate(search_results, 1):
            metadata = result.get("metadata", {})
            content = result.get("document", "")
            title = metadata.get("title", "未知文档")
            document_id = metadata.get("document_id", 0)
            distance = result.get("distance", 0.0)
            score = round(1.0 / (1.0 + distance), 4)
            
            context_parts.append(f"[资料{i}] 标题：{title}\n内容：{content}")
            sources.append({
                "document_id": document_id,
                "title": title,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "score": score
            })
        
        context = "\n\n".join(context_parts) if context_parts else "无相关资料"
        
        # 第三步：生成回答
        if self._use_local_llm:
            # 本地模式：直接调用本地LLM
            full_prompt = RAG_SYSTEM_PROMPT.format(context=context, question=question)
            
            # 打印发送给LLM的完整内容
            logger.info("=" * 80)
            logger.info("发送给大语言模型的完整内容:")
            logger.info("=" * 80)
            logger.info(full_prompt)
            logger.info("=" * 80)
            
            answer = self.llm.invoke(full_prompt)
            
            # 打印LLM的回答
            logger.info("大语言模型的回答:")
            logger.info("=" * 80)
            logger.info(answer)
            logger.info("=" * 80)
            
        elif not search_results:
            # 没有检索到相关文档
            answer = "抱歉，知识库中暂未找到相关信息。请尝试换个问题或联系管理员添加相关文档。"
        else:
            try:
                # 构造完整的 prompt（用于日志显示）
                full_prompt = RAG_SYSTEM_PROMPT.format(context=context, question=question)
                
                # 打印发送给LLM的完整内容
                logger.info("=" * 80)
                logger.info("发送给大语言模型的完整内容:")
                logger.info("=" * 80)
                logger.info(full_prompt)
                logger.info("=" * 80)
                
                # 使用RAG链生成回答
                answer = self.rag_chain.invoke(question)
                
                # 打印LLM的回答
                logger.info("大语言模型的回答:")
                logger.info("=" * 80)
                logger.info(answer)
                logger.info("=" * 80)
                
                
            except Exception as e:
                # LLM调用失败，返回检索到的资料
                answer = f"抱歉，问答服务暂时不可用。\n\n以下是知识库中找到的相关资料：\n\n{context}"
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def simple_query(self, question: str) -> str:
        """
        简化版问答，只返回回答文本
        
        Args:
            question: 用户问题
            
        Returns:
            回答文本
        """
        result = self.query(question)
        return result["answer"]


# 全局RAG服务实例
rag_service = RAGService()
