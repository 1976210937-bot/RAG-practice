"""
Pydantic 数据验证模型
定义API请求和响应的数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 用户相关 Schema ====================

class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    role: str = Field("user", description="角色：admin/user")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """更新用户请求"""
    email: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """登录令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== 文档相关 Schema ====================

class DocumentBase(BaseModel):
    """文档基础信息"""
    title: str = Field(..., description="文档标题")
    file_type: Optional[str] = Field(None, description="文件类型")


class DocumentResponse(DocumentBase):
    """文档响应"""
    id: int
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    chunk_count: int = 0
    status: str
    uploader_id: int
    uploader_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    total: int
    items: List[DocumentResponse]


# ==================== 对话相关 Schema ====================

class ConversationBase(BaseModel):
    """会话基础信息"""
    title: str = Field("新对话", description="会话标题")


class ConversationCreate(ConversationBase):
    """创建会话请求"""
    pass


class ConversationResponse(ConversationBase):
    """会话响应"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    """消息基础信息"""
    role: str = Field(..., description="角色：user/assistant")
    content: str = Field(..., description="消息内容")


class ChatMessageResponse(ChatMessageBase):
    """消息响应"""
    id: int
    conversation_id: int
    sources: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 问答相关 Schema ====================

class QueryRequest(BaseModel):
    """问答请求"""
    question: str = Field(..., description="问题")
    conversation_id: Optional[int] = Field(None, description="会话ID，不传则新建会话")


class SourceDocument(BaseModel):
    """引用的来源文档"""
    document_id: int
    title: str
    content: str
    score: float


class QueryResponse(BaseModel):
    """问答响应"""
    answer: str = Field(..., description="回答内容")
    conversation_id: int = Field(..., description="会话ID")
    sources: List[SourceDocument] = Field(default_factory=list, description="引用来源")


# ==================== 统计数据 Schema ====================

class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    user_count: int = Field(0, description="用户总数")
    document_count: int = Field(0, description="文档总数")
    conversation_count: int = Field(0, description="会话总数")
    message_count: int = Field(0, description="消息总数")
    today_new_users: int = Field(0, description="今日新增用户")
    today_new_documents: int = Field(0, description="今日新增文档")
    today_new_conversations: int = Field(0, description="今日新会话")
    today_new_messages: int = Field(0, description="今日新消息")
