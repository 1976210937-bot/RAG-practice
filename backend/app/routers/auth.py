"""
认证相关API路由
包含用户登录、注册、获取当前用户信息等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import UserLogin, Token, UserResponse, UserCreate
from app.utils.auth import (
    verify_password,
    create_access_token,
    get_current_user,
    md5_encrypt
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=Token, summary="用户登录")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    """
    # 查询用户
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    """
    return current_user


@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口（默认注册为普通用户）
    
    - **username**: 用户名
    - **password**: 密码
    - **email**: 邮箱（可选）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户（默认角色为user）
    db_user = User(
        username=user_create.username,
        password_hash=md5_encrypt(user_create.password),
        email=user_create.email,
        role="user",
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
