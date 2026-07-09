"""
管理员后台API路由
包含用户管理、系统统计等管理接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, Document, Conversation, ChatMessage
from app.schemas import UserResponse, UserCreate, UserUpdate, DashboardStats
from app.utils.auth import get_current_admin_user, md5_encrypt

router = APIRouter(prefix="/api/admin", tags=["管理员后台"])


# ==================== 统计数据接口 ====================

@router.get("/stats", response_model=DashboardStats, summary="获取仪表盘统计数据")
def get_dashboard_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取系统仪表盘统计数据（仅管理员）
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # 总数统计
    user_count = db.query(func.count(User.id)).scalar()
    document_count = db.query(func.count(Document.id)).scalar()
    conversation_count = db.query(func.count(Conversation.id)).scalar()
    message_count = db.query(func.count(ChatMessage.id)).scalar()
    
    # 今日新增统计
    today_new_users = db.query(func.count(User.id)).filter(
        User.created_at >= today,
        User.created_at < tomorrow
    ).scalar()
    
    today_new_documents = db.query(func.count(Document.id)).filter(
        Document.created_at >= today,
        Document.created_at < tomorrow
    ).scalar()
    
    today_new_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.created_at >= today,
        Conversation.created_at < tomorrow
    ).scalar()
    
    today_new_messages = db.query(func.count(ChatMessage.id)).filter(
        ChatMessage.created_at >= today,
        ChatMessage.created_at < tomorrow
    ).scalar()
    
    return DashboardStats(
        user_count=user_count or 0,
        document_count=document_count or 0,
        conversation_count=conversation_count or 0,
        message_count=message_count or 0,
        today_new_users=today_new_users or 0,
        today_new_documents=today_new_documents or 0,
        today_new_conversations=today_new_conversations or 0,
        today_new_messages=today_new_messages or 0
    )


# ==================== 用户管理接口 ====================

@router.get("/users", response_model=List[UserResponse], summary="获取用户列表")
def get_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有用户列表（仅管理员）
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.post("/users", response_model=UserResponse, summary="创建用户")
def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建新用户（仅管理员）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    db_user = User(
        username=user_create.username,
        password_hash=md5_encrypt(user_create.password),
        email=user_create.email,
        role=user_create.role,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}", response_model=UserResponse, summary="更新用户")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息（仅管理员）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.password is not None:
        user.password_hash = md5_encrypt(user_update.password)
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除用户（仅管理员）
    """
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}
