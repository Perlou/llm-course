"""
Mini-Dify - 知识库 API
"""

import os
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.config import get_settings
from app.models.dataset import Dataset, Document
from app.core.rag_service import (
    process_document,
    retrieve,
    get_collection_name,
    VectorStore,
)
from app.schemas import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    DocumentResponse,
    RetrieveRequest,
    RetrieveResponse,
    RetrieveResultItem,
)

router = APIRouter(prefix="/datasets", tags=["知识库管理"])
settings = get_settings()


# ==================== Dataset CRUD ====================


@router.post("", response_model=DatasetResponse, status_code=201)
async def create_dataset(data: DatasetCreate, db: AsyncSession = Depends(get_db)):
    """创建知识库"""
    dataset = Dataset(**data.model_dump())
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetResponse])
async def list_datasets(db: AsyncSession = Depends(get_db)):
    """获取知识库列表"""
    result = await db.execute(select(Dataset).order_by(Dataset.updated_at.desc()))
    return result.scalars().all()


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取知识库详情"""
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "知识库不存在")
    return dataset


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: UUID, data: DatasetUpdate, db: AsyncSession = Depends(get_db)
):
    """更新知识库配置"""
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "知识库不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dataset, key, value)
    await db.commit()
    await db.refresh(dataset)
    return dataset


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除知识库（同时删除 Milvus Collection）"""
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "知识库不存在")

    # 删除 Milvus Collection
    try:
        collection_name = get_collection_name(str(dataset_id))
        await VectorStore.drop_collection(collection_name)
    except Exception:
        pass  # Milvus 不可用时仍允许删除数据库记录

    await db.delete(dataset)
    await db.commit()


# ==================== Document Management ====================


@router.get("/{dataset_id}/documents", response_model=list[DocumentResponse])
async def list_documents(dataset_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取知识库下的文档列表"""
    result = await db.execute(
        select(Document)
        .where(Document.dataset_id == dataset_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


async def _process_document_task(
    file_path: str,
    file_type: str,
    document_id: str,
    dataset_id: str,
    chunk_size: int,
    chunk_overlap: int,
    db_url: str,
):
    """后台任务：处理文档（解析 → 切分 → 嵌入 → 存入 Milvus）"""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AS
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AS, expire_on_commit=False)

    async with async_session() as db:
        try:
            doc = await db.get(Document, document_id)
            if not doc:
                return

            doc.status = "processing"
            await db.commit()

            chunk_count = await process_document(
                file_path=file_path,
                file_type=file_type,
                document_id=document_id,
                dataset_id=dataset_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            doc.chunk_count = chunk_count
            doc.status = "completed"
            await db.commit()

            # 更新 Dataset 的 chunk_count
            dataset = await db.get(Dataset, dataset_id)
            if dataset:
                # 重新统计所有文档 chunk 数
                from sqlalchemy import func

                result = await db.execute(
                    select(func.sum(Document.chunk_count)).where(
                        Document.dataset_id == dataset_id,
                        Document.status == "completed",
                    )
                )
                total = result.scalar() or 0
                dataset.chunk_count = total
                await db.commit()

        except Exception as e:
            doc = await db.get(Document, document_id)
            if doc:
                doc.status = "failed"
                doc.error_msg = str(e)[:500]
                await db.commit()
        finally:
            await engine.dispose()


@router.post("/{dataset_id}/documents/upload")
async def upload_document(
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """上传文档到知识库"""
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "知识库不存在")

    # 验证文件类型
    filename = file.filename or "unknown.txt"
    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
    allowed_types = {"txt", "md", "pdf", "docx"}
    if file_type not in allowed_types:
        raise HTTPException(400, f"不支持的文件类型: {file_type}，仅支持 {allowed_types}")

    # 保存文件
    upload_dir = os.path.join(settings.upload_dir, str(dataset_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 创建文档记录
    doc = Document(
        dataset_id=dataset_id,
        name=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=len(content),
        status="pending",
    )
    db.add(doc)
    dataset.document_count += 1
    await db.commit()
    await db.refresh(doc)

    # 后台处理文档
    background_tasks.add_task(
        _process_document_task,
        file_path=file_path,
        file_type=file_type,
        document_id=str(doc.id),
        dataset_id=str(dataset_id),
        chunk_size=dataset.chunk_size,
        chunk_overlap=dataset.chunk_overlap,
        db_url=settings.database_url,
    )

    return {"id": str(doc.id), "name": doc.name, "status": "pending"}


@router.delete("/{dataset_id}/documents/{document_id}", status_code=204)
async def delete_document(
    dataset_id: UUID, document_id: UUID, db: AsyncSession = Depends(get_db)
):
    """删除文档（同时清理 Milvus 向量）"""
    doc = await db.get(Document, document_id)
    if not doc or doc.dataset_id != dataset_id:
        raise HTTPException(404, "文档不存在")

    # 删除 Milvus 中的向量
    try:
        collection_name = get_collection_name(str(dataset_id))
        await VectorStore.delete_by_document(collection_name, str(document_id))
    except Exception:
        pass

    dataset = await db.get(Dataset, dataset_id)
    if dataset:
        dataset.document_count = max(0, dataset.document_count - 1)
        dataset.chunk_count = max(0, dataset.chunk_count - doc.chunk_count)

    # 删除文件
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    await db.commit()


# ==================== Retrieval ====================


@router.post("/{dataset_id}/retrieve", response_model=RetrieveResponse)
async def retrieve_from_dataset(
    dataset_id: UUID,
    data: RetrieveRequest,
    db: AsyncSession = Depends(get_db),
):
    """向量检索"""
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "知识库不存在")

    raw_results = await retrieve(
        dataset_id=str(dataset_id),
        query=data.query,
        top_k=data.top_k,
    )

    # 获取文档名称
    doc_names: dict[str, str] = {}
    for r in raw_results:
        did = r["document_id"]
        if did not in doc_names:
            doc = await db.get(Document, did)
            doc_names[did] = doc.name if doc else "未知文档"

    results = [
        RetrieveResultItem(
            content=r["content"],
            score=r["score"],
            document_id=r["document_id"],
            document_name=doc_names.get(r["document_id"], ""),
            chunk_index=r["chunk_index"],
        )
        for r in raw_results
    ]

    return RetrieveResponse(query=data.query, results=results)
