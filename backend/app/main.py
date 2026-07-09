"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import auth, documents, chat, admin
from app.config import settings
import logging
import os

# 配置日志级别为 INFO，便于调试
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def init_db():
    """初始化数据库表"""
    # 创建所有数据表
    Base.metadata.create_all(bind=engine)
    
    # 创建必要的目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)


def create_default_admin():
    """创建默认管理员账号"""
    from app.database import SessionLocal
    from app.models import User
    from app.utils.auth import md5_encrypt
    
    db = SessionLocal()
    try:
        # 检查是否已有管理员
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            # 创建默认管理员
            default_admin = User(
                username="admin",
                password_hash=md5_encrypt("123456"),
                email="admin@example.com",
                role="admin",
                is_active=True
            )
            db.add(default_admin)
            db.commit()
            print("默认管理员账号已创建: admin / 123456")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("正在启动RAG知识库问答系统...")
    init_db()
    create_default_admin()
    print("系统启动完成！")
    yield
    # 关闭时执行
    print("系统正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="RAG企业内部知识库问答系统",
    description="基于LangChain + Chroma + DeepSeek的企业知识库问答系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/", tags=["根路径"])
def root():
    """根路径，返回系统信息"""
    return {
        "name": "RAG企业内部知识库问答系统",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
