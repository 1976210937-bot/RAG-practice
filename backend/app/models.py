"""
数据库模型定义模块
定义用户、文档、对话记录等数据表结构
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(32), nullable=False, comment="MD5加密后的密码")
    email = Column(String(100), comment="邮箱")
    role = Column(String(20), default="user", comment="角色：admin-管理员，user-普通用户")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    documents = relationship("Document", back_populates="uploader")
    conversations = relationship("Conversation", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Document(Base):
    """知识库文档表模型"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True, comment="文档ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    file_name = Column(String(200), comment="原始文件名")
    file_path = Column(String(500), comment="文件存储路径")
    file_type = Column(String(50), comment="文件类型：txt/md/pdf等")
    file_size = Column(Integer, comment="文件大小（字节）")
    content = Column(Text, comment="文档内容")
    chunk_count = Column(Integer, default=0, comment="分块数量")
    status = Column(String(20), default="pending", comment="状态：pending-待处理，processing-处理中，completed-已完成，failed-失败")
    uploader_id = Column(Integer, ForeignKey("users.id"), comment="上传者ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    uploader = relationship("User", back_populates="documents")


class Conversation(Base):
    """会话表模型"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True, comment="会话ID")
    title = Column(String(200), default="新对话", comment="会话标题")
    user_id = Column(Integer, ForeignKey("users.id"), comment="用户ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    """聊天消息表模型"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True, comment="消息ID")
    conversation_id = Column(Integer, ForeignKey("conversations.id"), comment="会话ID")
    user_id = Column(Integer, ForeignKey("users.id"), comment="用户ID")
    role = Column(String(20), nullable=False, comment="角色：user-用户，assistant-助手")
    content = Column(Text, nullable=False, comment="消息内容")
    sources = Column(Text, comment="引用的来源文档（JSON格式）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")
