"""
文档管理API路由
包含文档上传、列表查询、删除等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models import User, Document
from app.schemas import DocumentResponse, DocumentListResponse
from app.utils.auth import get_current_user, get_current_admin_user
from app.config import settings
from app.services.document_service import document_processor
from app.services.vector_store_service import vector_store_service
import os
import uuid
import threading
from datetime import datetime

router = APIRouter(prefix="/api/documents", tags=["文档管理"])


@router.get("", response_model=DocumentListResponse, summary="获取文档列表")
def get_documents(
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取文档列表（分页）
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **keyword**: 搜索关键词（可选）
    """
    query = db.query(Document)
    
    # 关键词搜索
    if keyword:
        query = query.filter(Document.title.contains(keyword))
    
    # 普通用户只能看到已完成的文档
    if current_user.role != "admin":
        query = query.filter(Document.status == "completed")
    
    # 总数
    total = query.count()
    
    # 分页
    skip = (page - 1) * page_size
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(page_size).all()
    
    # 构造响应
    items = []
    for doc in documents:
        doc_dict = DocumentResponse.model_validate(doc).model_dump()
        doc_dict["uploader_name"] = doc.uploader.username if doc.uploader else ""
        items.append(DocumentResponse(**doc_dict))
    
    return DocumentListResponse(total=total, items=items)


@router.get("/{doc_id}", response_model=DocumentResponse, summary="获取文档详情")
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个文档详情
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 普通用户只能查看已完成的文档
    if current_user.role != "admin" and doc.status != "completed":
        raise HTTPException(status_code=403, detail="无权查看该文档")
    
    doc_dict = DocumentResponse.model_validate(doc).model_dump()
    doc_dict["uploader_name"] = doc.uploader.username if doc.uploader else ""
    
    return DocumentResponse(**doc_dict)


@router.post("/upload", response_model=DocumentResponse, summary="上传文档")
async def upload_document(
    title: str = Form(..., description="文档标题"),
    file: UploadFile = File(..., description="上传的文件"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    上传文档（仅管理员可上传）
    
    支持txt、md等文本文件，上传后会自动处理并加入向量库
    """
    # 验证文件大小
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 读取文件内容（仅文本文件）
    file_content = ""
    if file_ext.lower() in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.csv']:
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                file_content = content.decode('gbk')
            except UnicodeDecodeError:
                file_content = ""
    
    # 创建文档记录
    doc = Document(
        title=title,
        file_name=file.filename,
        file_path=file_path,
        file_type=file_ext.lower().lstrip('.'),
        file_size=file_size,
        content=file_content,
        status="pending",
        uploader_id=current_user.id
    )
    
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # 异步处理文档（分块+向量化）
    def process_async(doc_id):
        document_processor.process_document(doc_id)
    
    threading.Thread(target=process_async, args=(doc.id,), daemon=True).start()
    
    doc_dict = DocumentResponse.model_validate(doc).model_dump()
    doc_dict["uploader_name"] = current_user.username
    
    return DocumentResponse(**doc_dict)


@router.delete("/{doc_id}", summary="删除文档")
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除文档（仅管理员可删除）
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 删除向量库中的相关向量
    try:
        document_processor.delete_document_vectors(doc_id)
    except Exception:
        pass
    
    # 删除物理文件
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass
    
    db.delete(doc)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/{doc_id}/reprocess", response_model=DocumentResponse, summary="重新处理文档")
def reprocess_document(
    doc_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    重新处理文档（重新分块并向量化，仅管理员）
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 先删除旧的向量
    try:
        document_processor.delete_document_vectors(doc_id)
    except Exception:
        pass
    
    # 重置状态
    doc.status = "pending"
    doc.chunk_count = 0
    db.commit()
    
    # 异步重新处理
    def process_async(d_id):
        document_processor.process_document(d_id)
    
    threading.Thread(target=process_async, args=(doc_id,), daemon=True).start()
    
    db.refresh(doc)
    doc_dict = DocumentResponse.model_validate(doc).model_dump()
    doc_dict["uploader_name"] = doc.uploader.username if doc.uploader else ""
    
    return DocumentResponse(**doc_dict)
