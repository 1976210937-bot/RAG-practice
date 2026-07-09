"""
对话与问答API路由
包含会话管理、问答接口等
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import User, Conversation, ChatMessage, Document
from app.schemas import (
    ConversationResponse,
    ConversationCreate,
    ChatMessageResponse,
    QueryRequest,
    QueryResponse,
    SourceDocument
)
from app.utils.auth import get_current_user
from app.services.rag_service import rag_service
import json

router = APIRouter(prefix="/api/chat", tags=["对话问答"])


@router.get("/conversations", response_model=List[ConversationResponse], summary="获取会话列表")
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有会话列表
    """
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return conversations


@router.post("/conversations", response_model=ConversationResponse, summary="创建会话")
def create_conversation(
    conv_create: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建一个新的会话
    """
    conversation = Conversation(
        title=conv_create.title,
        user_id=current_user.id
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/conversations/{conv_id}/messages", response_model=List[ChatMessageResponse], summary="获取会话消息")
def get_conversation_messages(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定会话的所有消息
    """
    # 验证会话归属
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conv_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return messages


@router.delete("/conversations/{conv_id}", summary="删除会话")
def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定会话
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    db.delete(conversation)
    db.commit()
    return {"message": "删除成功"}


@router.post("/query", response_model=QueryResponse, summary="提问接口")
def query(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    向知识库提问并获取回答
    
    - **question**: 用户问题
    - **conversation_id**: 会话ID（可选，不传则新建会话）
    """
    # 获取或创建会话
    if query_request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == query_request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
    else:
        # 创建新会话（使用问题的前20个字作为标题）
        title = query_request.question[:20] + "..." if len(query_request.question) > 20 else query_request.question
        conversation = Conversation(title=title, user_id=current_user.id)
        db.add(conversation)
        db.flush()
    
    # 保存用户消息
    user_message = ChatMessage(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="user",
        content=query_request.question
    )
    db.add(user_message)
    db.flush()
    
    # 调用RAG服务进行问答
    rag_result = rag_service.query(query_request.question)
    answer = rag_result["answer"]
    sources_data = rag_result["sources"]
    
    # 构造SourceDocument列表
    sources = [SourceDocument(**src) for src in sources_data]
    
    # 保存助手消息
    assistant_message = ChatMessage(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="assistant",
        content=answer,
        sources=json.dumps([s.model_dump() for s in sources], ensure_ascii=False) if sources else None
    )
    db.add(assistant_message)
    
    # 更新会话时间
    conversation.updated_at = func.now()
    
    db.commit()
    db.refresh(conversation)
    
    return QueryResponse(
        answer=answer,
        conversation_id=conversation.id,
        sources=sources
    )
