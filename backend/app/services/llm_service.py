"""
LLM大语言模型服务模块
封装DeepSeek Chat模型，支持本地降级方案
"""
from typing import Any
from app.config import settings


class LocalLLMService:
    """
    本地简易LLM服务（降级方案）
    返回预设的模拟回答，用于演示和开发环境
    """
    
    def __init__(self):
        """初始化本地LLM服务"""
        pass
    
    def get_llm(self):
        """获取本地模拟LLM实例"""
        return self
    
    def invoke(self, prompt: str) -> str:
        """
        模拟LLM调用，返回预设回答
        
        Args:
            prompt: 提示词
            
        Returns:
            模拟回答文本
        """
        # 从提示词中提取问题部分
        question_start = prompt.find("用户的问题：")
        if question_start != -1:
            question = prompt[question_start + 5:].strip()
        else:
            question = "您的问题"
        
        return f"""这是一个模拟回答（开发环境）。
        
您的问题：{question}

由于尚未配置有效的DeepSeek API Key，当前使用本地模拟模式。

在生产环境中，系统会通过DeepSeek大语言模型基于知识库中的文档内容为您提供准确的回答。

如需使用真实的大语言模型，请在后端配置文件中设置有效的API Key。"""


class LLMService:
    """
    LLM大语言模型服务类
    使用DeepSeek的Chat模型，通过OpenAI兼容接口调用
    """
    
    def __init__(self):
        """初始化LLM服务"""
        self._llm = None
        self._local_llm = LocalLLMService()
        self._use_local = False
        
        # 检查API Key是否配置
        if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == 'your-deepseek-api-key-here':
            print("警告：未配置DeepSeek API Key，使用本地降级方案")
            self._use_local = True
            return
        
        # 尝试初始化DeepSeek LLM
        try:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=settings.DEEPSEEK_MODEL,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.7,
                max_tokens=2048
            )
        except Exception as e:
            print(f"初始化DeepSeek LLM失败，使用本地降级方案: {e}")
            self._use_local = True
    
    def get_llm(self):
        """获取LangChain的LLM实例"""
        if self._use_local or self._llm is None:
            return self._local_llm
        return self._llm
    
    def invoke(self, prompt: str) -> str:
        """
        直接调用LLM生成回答
        
        Args:
            prompt: 提示词
            
        Returns:
            LLM生成的回答文本
        """
        if self._use_local or self._llm is None:
            return self._local_llm.invoke(prompt)
        
        try:
            response = self._llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"调用DeepSeek LLM失败，降级使用本地方案: {e}")
            return self._local_llm.invoke(prompt)


# 全局LLM服务实例
llm_service = LLMService()
