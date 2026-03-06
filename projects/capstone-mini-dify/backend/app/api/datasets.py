"""
Mini-Dify - 知识库 API
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.dataset import Dataset, Document
from app.schemas import DatasetCreate, DatasetUpdate, DatasetResponse, DocumentResponse

router = APIRouter(prefix="/datasets", tags=["知识库管理"])


@router.post("", response_model=DatasetResponse, status_code=201)
async def create_dataset(data: DatasetCreate, db: AsyncSession = Depends(get_db)):
    """创建知识库"""
    dataset = Dataset(**data.model_dump())
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    # TODO: 创建 Milvus Collection
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
    """删除知识库"""
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "知识库不存在")
    await db.delete(dataset)
    await db.commit()
    # TODO: 删除 Milvus Collection


@router.get("/{dataset_id}/documents", response_model=list[DocumentResponse])
async def list_documents(dataset_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取知识库下的文档列表"""
    result = await db.execute(
        select(Document)
        .where(Document.dataset_id == dataset_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{dataset_id}/documents/upload")
async def upload_document(
    dataset_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """上传文档到知识库"""
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "知识库不存在")

    # TODO: 保存文件、解析、切分、嵌入、写入 Milvus
    doc = Document(
        dataset_id=dataset_id,
        name=file.filename,
        file_type=file.filename.rsplit(".", 1)[-1]
        if "." in file.filename
        else "unknown",
        file_size=file.size,
        status="pending",
    )
    db.add(doc)
    dataset.document_count += 1
    await db.commit()
    await db.refresh(doc)

    return {"id": str(doc.id), "name": doc.name, "status": doc.status}


@router.delete("/{dataset_id}/documents/{document_id}", status_code=204)
async def delete_document(
    dataset_id: UUID, document_id: UUID, db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    doc = await db.get(Document, document_id)
    if not doc or doc.dataset_id != dataset_id:
        raise HTTPException(404, "文档不存在")

    dataset = await db.get(Dataset, dataset_id)
    if dataset:
        dataset.document_count = max(0, dataset.document_count - 1)
        dataset.chunk_count = max(0, dataset.chunk_count - doc.chunk_count)

    await db.delete(doc)
    await db.commit()
    # TODO: 删除 Milvus 中的向量
